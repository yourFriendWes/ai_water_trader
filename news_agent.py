#!/usr/bin/env python3
"""
News Agent for Climate Events in Colorado Basin States
Searches for recent climate/weather/disaster news using OpenAI WebSearchTool
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class NewsAgent:
    """OpenAI Agent for searching climate-related news in Colorado Basin states"""
    
    def __init__(self):
        """Initialize the news agent"""
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = os.getenv('NEWS_AGENT_MODEL', 'gpt-4o')
        
        # Colorado Basin states
        self.target_states = [
            'Wyoming', 'California', 'Nevada', 'Utah', 
            'Colorado', 'Arizona', 'New Mexico'
        ]
        
        # Climate-related keywords
        self.keywords = [
            'wildfire', 'drought', 'flood', 'heatwave', 
            'storm', 'forecast', 'weather', 'climate'
        ]
        
        # Configure web search tool for US region (Colorado Basin states)
        self.web_search_tool = {
            "type": "web_search_preview",
            "user_location": {
                "type": "approximate",
                "country": "US",
                "region": "Colorado Basin"
            },
            "search_context_size": "medium"
        }
        
        # System instructions for climate news focus
        self.system_instructions = f"""
        You are a climate news analyst specializing in the Colorado Basin region.
        
        Focus strictly on recent (within the past 7-10 days) climate-related news for these states:
        {', '.join(self.target_states)}
        
        Search for news about: {', '.join(self.keywords)}
        
        Provide concise summaries with:
        - State-specific climate events
        - Reliable source citations
        - Recent dates (within last 7-10 days)
        - Impact assessment where relevant
        
        Format your response as a brief daily briefing suitable for decision-makers.
        """
        
    def test_configuration(self):
        """Test that the agent is properly configured"""
        try:
            print(f"✓ OpenAI client initialized: {self.client is not None}")
            print(f"✓ Model configured: {self.model}")
            print(f"✓ Target states: {len(self.target_states)} states")
            print(f"✓ Keywords: {len(self.keywords)} keywords")
            print(f"✓ Web search tool configured: {self.web_search_tool['type']}")
            print(f"✓ System instructions ready: {len(self.system_instructions.strip())} characters")
            return True
        except Exception as e:
            print(f"❌ Configuration error: {str(e)}")
            return False
    
    def search_climate_news(self, query=None):
        """Search for climate news in Colorado Basin region"""
        if query is None:
            query = "Give me the latest news on climate or weather events in the Colorado Basin region."
        
        print(f"🔍 Searching for climate news...")
        print(f"📅 Target timeframe: Last 7-10 days")
        print(f"🌎 Target states: {', '.join(self.target_states)}")
        
        # Use Responses API with web search
        try:
            response = self.client.responses.create(
                model=self.model,
                tools=[self.web_search_tool],
                input=f"{self.system_instructions}\n\nQuery: {query}"
            )
            return response.output_text
        except Exception as e:
            error_msg = f"API call failed: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg


def main():
    """Main function for testing the news agent"""
    print("🌊 Climate News Agent - Colorado Basin States")
    print("=" * 50)
    
    try:
        print("\n🔧 Testing Configuration...")
        agent = NewsAgent()
        config_ok = agent.test_configuration()
        
        if config_ok:
            print(f"\n🔍 Testing Search Functionality...")
            result = agent.search_climate_news()
            print(f"\n📰 Results:\n{result}")
        else:
            print("❌ Configuration test failed - skipping search test")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()