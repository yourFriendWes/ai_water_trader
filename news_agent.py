#!/usr/bin/env python3
"""
Climate Events Agent for Imperial Irrigation District
Searches for recent climate events, weather disasters, and natural phenomena
FOCUS: Climate events only - NOT policy or water management regulations
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class NewsAgent:
    """OpenAI Agent for searching climate events affecting Imperial Irrigation District operations"""
    
    def __init__(self):
        """Initialize the news agent"""
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = os.getenv('NEWS_AGENT_MODEL', 'gpt-4o')
        
        # Colorado Basin states (prioritized for Imperial Irrigation District)
        self.target_states = [
            'Wyoming', 'California', 'Nevada', 'Utah', 
            'Colorado', 'Arizona', 'New Mexico'
        ]
        
        # Imperial Irrigation District priority regions
        self.priority_regions = [
            'Imperial Valley', 'Southern California', 'Colorado River',
            'Salton Sea', 'Imperial County', 'Coachella Valley'
        ]
        
        # Climate-related keywords
        self.keywords = [
            'wildfire', 'drought', 'flood', 'heatwave', 
            'storm', 'forecast', 'weather', 'climate'
        ]
        
        # Configure web search tool for Imperial Valley/Southern CA focus
        self.web_search_tool = {
            "type": "web_search_preview",
            "user_location": {
                "type": "approximate",
                "country": "US",
                "region": "Imperial Valley",
                "city": "El Centro"
            },
            "search_context_size": "medium"
        }
        
        # System instructions for climate events focus
        self.system_instructions = f"""
        You are a climate events analyst specializing in weather and natural disasters for the Imperial Irrigation District.
        
        PRIMARY FOCUS: CLIMATE EVENTS affecting Imperial Valley, Southern California, and Colorado River basin.
        Priority regions: {', '.join(self.priority_regions)}
        
        Secondary focus: Colorado Basin states: {', '.join(self.target_states)}
        Climate event keywords: {', '.join(self.keywords)}
        
        FOCUS ONLY ON CLIMATE/WEATHER EVENTS, NOT POLICY OR WATER MANAGEMENT DECISIONS.
        
        For each climate event, assess RELEVANCE TO IMPERIAL IRRIGATION DISTRICT OPERATIONS (Score 1-10):
        - 10: Direct weather impact on Imperial Valley (extreme heat, flooding, storms)
        - 8-9: Colorado River basin events affecting water supply (drought, snowpack, flooding)
        - 6-7: Regional climate events that could impact agriculture or water availability
        - 4-5: General weather patterns with potential operational impact
        - 1-3: Minimal relevance to Imperial Irrigation District operations
        
        EXCLUDE: Water policy, regulations, agreements, political decisions
        INCLUDE: Wildfires, droughts, floods, storms, extreme temperatures, precipitation patterns
        
        ONLY include climate events scoring 6+ in your response.
        Prioritize recent events (within 7-10 days) that could affect operations.
        """
        
    def evaluate_relevance(self, climate_event):
        """Evaluate climate event relevance to Imperial Irrigation District operations (1-10 score)"""
        try:
            relevance_prompt = f"""
            Rate this CLIMATE EVENT's relevance to Imperial Irrigation District operations (1-10):
            
            Climate Event: {climate_event}
            
            Scoring criteria (EVENTS ONLY, NOT POLICY):
            - 10: Direct weather impact on Imperial Valley (extreme heat, flooding, storms)
            - 8-9: Colorado River basin climate events affecting water supply (drought, snowpack, flooding)
            - 6-7: Regional climate events that could impact agriculture or water availability  
            - 4-5: General weather patterns with potential operational impact
            - 1-3: Minimal relevance to Imperial Irrigation District operations
            
            If this is a POLICY/REGULATION item (not a climate event), return 0.
            Return only the numerical score (0-10).
            """
            
            response = self.client.responses.create(
                model=self.model,
                input=relevance_prompt
            )
            
            # Extract numerical score from response
            score_text = response.output_text.strip()
            score = int(score_text) if score_text.isdigit() else 5
            return max(1, min(10, score))  # Ensure score is 1-10
            
        except Exception as e:
            print(f"⚠️ Relevance scoring failed: {str(e)}")
            return 5  # Default to moderate relevance
    
    def test_configuration(self):
        """Test that the agent is properly configured"""
        try:
            print(f"✓ OpenAI client initialized: {self.client is not None}")
            print(f"✓ Model configured: {self.model}")
            print(f"✓ Target states: {len(self.target_states)} states")
            print(f"✓ Priority regions: {len(self.priority_regions)} regions")
            print(f"✓ Keywords: {len(self.keywords)} keywords")
            print(f"✓ Web search tool configured: {self.web_search_tool['type']}")
            print(f"✓ System instructions ready: {len(self.system_instructions.strip())} characters")
            return True
        except Exception as e:
            print(f"❌ Configuration error: {str(e)}")
            return False
    
    def search_climate_news(self, query=None, relevance_threshold=6):
        """Search for climate events with Imperial Irrigation District operational relevance filtering"""
        if query is None:
            query = "Latest climate events, weather disasters, droughts, floods, wildfires, and extreme weather in Imperial Valley, Colorado River basin, and Southern California. Articles related to longer term climate news may also be considered."
        
        print(f"🌡️ Searching for Imperial Irrigation District relevant climate events...")
        print(f"📅 Target timeframe: Last 7-10 days")
        print(f"🌎 Priority regions: {', '.join(self.priority_regions)}")
        print(f"📊 Relevance threshold: {relevance_threshold}+ (operational impact)")
        print(f"⚠️  FOCUS: Climate events only - NOT policy or regulations")
        
        # Use Responses API with web search and climate events focus
        try:
            response = self.client.responses.create(
                model=self.model,
                tools=[self.web_search_tool],
                input=f"{self.system_instructions}\n\nQuery: {query}\n\nFilter for climate events with relevance score {relevance_threshold}+ only. EXCLUDE policy and regulatory news."
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