#!/usr/bin/env python3
"""
Climate Events Agent for Imperial Irrigation District
Searches for recent climate events, weather disasters, and natural phenomena
FOCUS: Climate events only - NOT policy or water management regulations
"""

import os
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
    
    def get_article_urls(self, headline_summary):
        """Extract full article URLs from headlines and summaries for deep reading"""
        try:
            url_extraction_prompt = f"""
            From this climate news summary, identify the full article URLs that should be read in detail:
            
            Summary: {headline_summary}
            
            Return ONLY the URLs (one per line) for articles that:
            1. Score 8+ relevance to Imperial Irrigation District operations
            2. Contain detailed climate event information (not just headlines)
            3. Are from reliable news sources
            
            Format: Return URLs only, one per line.
            """
            
            response = self.client.responses.create(
                model=self.model,
                tools=[self.web_search_tool],
                input=url_extraction_prompt
            )
            
            # Parse URLs from response
            urls = []
            for line in response.output_text.strip().split('\n'):
                line = line.strip()
                if line.startswith('http'):
                    urls.append(line)
            
            return urls[:3]  # Limit to top 3 most relevant articles
            
        except Exception as e:
            print(f"⚠️ URL extraction failed: {str(e)}")
            return []
    
    def read_full_article(self, url):
        """Read and analyze full article content for detailed climate event intelligence"""
        try:
            article_analysis_prompt = f"""
            Read this full article and extract detailed Imperial Irrigation District operational intelligence:
            
            URL: {url}
            
            Focus on extracting:
            1. Specific climate event details (temperatures, precipitation, duration)
            2. Geographic impact areas (Imperial Valley, Colorado River, Southern CA)
            3. Operational implications for water/agriculture/energy systems
            4. Timeline of events and forecasted impacts
            5. Any mention of water supply, irrigation, or agricultural effects
            
            Provide a detailed summary focusing on actionable operational information.
            Exclude policy discussions - focus only on the climate event itself.
            """
            
            response = self.client.responses.create(
                model=self.model,
                tools=[self.web_search_tool],
                input=article_analysis_prompt
            )
            
            return response.output_text
            
        except Exception as e:
            print(f"⚠️ Article reading failed for {url}: {str(e)}")
            return f"Unable to read full article: {url}"
    
    def extract_operational_insights(self, article_content):
        """Extract specific operational insights for Imperial Irrigation District from article content"""
        try:
            insights_prompt = f"""
            From this climate event article, extract SPECIFIC operational insights for Imperial Irrigation District:
            
            Article Content: {article_content}
            
            Extract and format as structured intelligence:
            
            ## IMMEDIATE OPERATIONAL IMPACTS:
            - [List specific impacts on water delivery, agriculture, energy]
            
            ## GEOGRAPHIC SCOPE:
            - [Specific areas affected: Imperial Valley, Colorado River, etc.]
            
            ## TIMELINE:
            - [When events started, duration, forecasted end]
            
            ## QUANTITATIVE DATA:
            - [Temperatures, precipitation amounts, water levels, etc.]
            
            ## RECOMMENDED ACTIONS:
            - [Specific operational adjustments based on climate event]
            
            Focus only on actionable intelligence that helps Imperial Irrigation District operations.
            """
            
            response = self.client.responses.create(
                model=self.model,
                input=insights_prompt
            )
            
            return response.output_text
            
        except Exception as e:
            print(f"⚠️ Insights extraction failed: {str(e)}")
            return "Unable to extract operational insights"
    
    def deep_analysis_search(self, query=None, relevance_threshold=8):
        """Perform deep article analysis for high-relevance climate events"""
        print(f"🔬 Starting deep analysis search for Imperial Irrigation District...")
        print(f"📊 Deep analysis threshold: {relevance_threshold}+ (high-relevance only)")
        
        # Step 1: Get initial headlines
        headlines = self.search_climate_news(query, relevance_threshold)
        print(f"\n📰 Initial Headlines Retrieved")
        
        # Step 2: Extract URLs for deep reading
        print(f"🔗 Extracting article URLs for deep analysis...")
        urls = self.get_article_urls(headlines)
        print(f"✓ Found {len(urls)} articles for deep reading")
        
        if not urls:
            return f"Headlines Summary:\n{headlines}\n\nNo articles identified for deep analysis."
        
        # Step 3: Read and analyze full articles
        deep_insights = []
        for i, url in enumerate(urls, 1):
            print(f"📖 Reading article {i}/{len(urls)}: {url[:50]}...")
            article_content = self.read_full_article(url)
            operational_insights = self.extract_operational_insights(article_content)
            deep_insights.append({
                'url': url,
                'content': article_content,
                'insights': operational_insights
            })
        
        # Step 4: Summarize actionable intelligence
        summary = self.summarize_actionable_intelligence(headlines, deep_insights)
        return summary
    
    def summarize_actionable_intelligence(self, headlines, deep_insights):
        """Summarize actionable intelligence comparing surface headlines vs deep analysis"""
        try:
            summary_prompt = f"""
            Create an Imperial Irrigation District climate intelligence briefing comparing surface headlines with deep article analysis:
            
            SURFACE HEADLINES:
            {headlines}
            
            DEEP ARTICLE ANALYSIS:
            {[insight['insights'] for insight in deep_insights]}
            
            Create a briefing with:
            
            ## EXECUTIVE SUMMARY
            [Key climate events affecting Imperial Irrigation District operations]
            
            ## DEEP ANALYSIS
            [What headlines missed that deep reading revealed]
            
            ## CRITICAL OPERATIONAL INTELLIGENCE
            [Specific actionable information for Imperial Irrigation District operations]
            
            ## IMMEDIATE ACTION ITEMS
            [Specific operational adjustments recommended]
            
            Focus on actionable intelligence that goes beyond surface-level headlines.
            """
            
            response = self.client.responses.create(
                model=self.model,
                input=summary_prompt
            )
            
            return response.output_text
            
        except Exception as e:
            print(f"⚠️ Intelligence summary failed: {str(e)}")
            return f"Headlines: {headlines}\n\nDeep Analysis: Available but summary failed"
    
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
    print("🌊 Climate Events Agent - Imperial Irrigation District")
    print("=" * 60)
    
    try:
        print("\n🔧 Testing Configuration...")
        agent = NewsAgent()
        config_ok = agent.test_configuration()
        
        if config_ok:
            print(f"\n🔍 Testing Basic Search Functionality...")
            basic_result = agent.search_climate_news()
            print(f"\n📰 Basic Results:\n{basic_result[:500]}...")
            
            print(f"\n🔬 Testing Deep Analysis Functionality...")
            deep_result = agent.deep_analysis_search()
            print(f"\n📊 Deep Analysis Results:\n{deep_result}")
        else:
            print("❌ Configuration test failed - skipping search test")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()