#!/usr/bin/env python3
"""
Water Arbitrage AI System - 6 Hour Sprint Version
Uses Python for processing + Google Sheets for storage/dashboard
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import openai
import time
import requests
from datetime import datetime, timedelta
import time
import json
import os
from dotenv import load_dotenv
from api_driver import APIDriver

load_dotenv()

class WaterArbitrageSystem:
    def __init__(self, sheet_url=None, openai_key=None):
        """Initialize the system with Google Sheets and OpenAI"""
        # Get credentials from environment variables
        sheet_url = sheet_url or os.getenv('GOOGLE_SHEET_URL')
        openai_key = openai_key or os.getenv('OPENAI_API_KEY')
        
        if not sheet_url:
            raise ValueError("GOOGLE_SHEET_URL must be provided or set in environment")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY must be provided or set in environment")
        # Setup Google Sheets
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        
        # Load credentials (you need to download this from Google Cloud Console)
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        self.client = gspread.authorize(creds)
        self.workbook = self.client.open_by_url(sheet_url)

        # Setup OpenAI
        openai.api_key = openai_key
        
        # Setup google sheet
        self.setup_sheets()
        
    def setup_sheets(self):
        """Create necessary worksheets"""
        sheet_names = ['RawData', 'AIAnalysis', 'Opportunities', 'Dashboard']
        
        for name in sheet_names:
            try:
                setattr(self, f"{name.lower()}_sheet", self.workbook.worksheet(name))
            except gspread.WorksheetNotFound:
                new_sheet = self.workbook.add_worksheet(title=name, rows="1000", cols="20")
                setattr(self, f"{name.lower()}_sheet", new_sheet)
        
        # Setup headers
        self.rawdata_sheet.update('A1:E1', [['Location', 'Price', 'Volume', 'Date', 'Type']])
        self.opportunities_sheet.update('A1:G1', [['Buy Location', 'Buy Price', 'Sell Location', 'Sell Price', 'Profit', 'Risk Score', 'Timestamp']])

    def collect_water_data(self):
        """Collect water market data from various sources"""
        print("📊 Collecting water market data...")
        
        # Mock water market data (replace with real APIs)
        base_data = [
            {'location': 'Central Valley', 'base_price': 450, 'volume': 1000, 'type': 'Surface'},
            {'location': 'Southern CA', 'base_price': 680, 'volume': 800, 'type': 'Surface'},
            {'location': 'Bay Area', 'base_price': 750, 'volume': 600, 'type': 'Surface'},
            {'location': 'Sacramento Valley', 'base_price': 520, 'volume': 900, 'type': 'Groundwater'},
            {'location': 'Imperial Valley', 'base_price': 380, 'volume': 1200, 'type': 'Colorado River'},
        ]
        
        # Add some realistic variation
        import random
        current_data = []
        for item in base_data:
            variation = random.uniform(0.9, 1.1)  # ±10% variation
            current_price = item['base_price'] * variation
            
            current_data.append([
                item['location'],
                round(current_price, 2),
                item['volume'],
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                item['type']
            ])
        
        # Add to Google Sheets
        self.rawdata_sheet.append_rows(current_data)
        
        return current_data

    def get_weather_impact(self, location):
        """Get weather data that impacts water demand"""
        # Mock weather API call (replace with real OpenWeatherMap API)
        weather_impacts = {
            'Central Valley': {'temp': 95, 'humidity': 30, 'drought_risk': 0.7},
            'Southern CA': {'temp': 88, 'humidity': 45, 'drought_risk': 0.8},
            'Bay Area': {'temp': 72, 'humidity': 65, 'drought_risk': 0.3},
            'Sacramento Valley': {'temp': 89, 'humidity': 40, 'drought_risk': 0.5},
            'Imperial Valley': {'temp': 102, 'humidity': 25, 'drought_risk': 0.6}
        }
        
        return weather_impacts.get(location, {'temp': 80, 'humidity': 50, 'drought_risk': 0.5})

    def analyze_with_ai(self):
        """Use AI to analyze market conditions"""
        print("🤖 Running AI market analysis...")
        
        # Get recent data from sheets
        all_data = self.rawdata_sheet.get_all_records()
        recent_data = all_data[-20:] if len(all_data) > 20 else all_data  # Last 20 records
        
        # Create analysis prompt
        df = pd.DataFrame(recent_data)
        summary_stats = df.groupby('Location').agg({
            'Price': ['mean', 'min', 'max', 'count'],
            'Volume': 'sum'
        }).round(2)
        
        prompt = f"""
        Analyze this water market data for arbitrage opportunities:
        
        Recent Transactions:
        {df.tail(10).to_string()}
        
        Market Summary by Location:
        {summary_stats.to_string()}
        
        Please provide:
        1. Top 3 arbitrage opportunities with specific buy/sell locations
        2. Risk factors to consider
        3. Optimal timing for trades
        4. Expected profit margins
        5. Market trend predictions
        
        Be specific about locations, prices, and profit calculations.
        """
        
        try:
            # response = openai.ChatCompletion.create(
            #     model="gpt-3.5-turbo",
            #     messages=[{"role": "user", "content": prompt}],
            #     max_tokens=600
            # )

            response = openai.chat.completions.create(model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600) 
            analysis = response.choices[0].message.content
            
            # Save analysis to sheets
            self.aianalysis_sheet.append_row([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                analysis
            ])
            
            return analysis
            
        except Exception as e:
            error_msg = f"AI analysis failed: {str(e)}"
            print(error_msg)
            return error_msg

    def detect_arbitrage_opportunities(self):
        """Detect arbitrage opportunities using rule-based logic"""
        print("🎯 Detecting arbitrage opportunities...")
        
        # Get current data
        all_data = self.rawdata_sheet.get_all_records()
        df = pd.DataFrame(all_data)
        
        if len(df) < 2:
            return []
        
        # Get latest price for each location
        df['Date'] = pd.to_datetime(df['Date'])
        latest_prices = df.sort_values('Date').groupby('Location').tail(1)
        
        opportunities = []
        
        # Find geographic arbitrage opportunities
        for i, row1 in latest_prices.iterrows():
            for j, row2 in latest_prices.iterrows():
                if i != j:
                    try:
                        buy_price = float(row1['Price'])
                        sell_price = float(row2['Price'])
                        profit = sell_price - buy_price
                        profit_margin = (profit / buy_price) * 100
                        
                        # Criteria for viable arbitrage
                        if profit > 50 and profit_margin > 10:  # $50+ profit, 10%+ margin
                            
                            # Calculate risk score
                            risk_score = self.calculate_risk_score(row1, row2, profit_margin)
                            
                            # Estimate transportation costs (mock)
                            transport_cost = self.estimate_transport_cost(row1['Location'], row2['Location'])
                            net_profit = profit - transport_cost
                            
                            if net_profit > 20:  # Must be profitable after transport
                                opportunities.append([
                                    row1['Location'],  # Buy location
                                    buy_price,        # Buy price
                                    row2['Location'], # Sell location
                                    sell_price,      # Sell price  
                                    round(net_profit, 2),  # Net profit per unit
                                    round(risk_score, 2),  # Risk score
                                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                ])
                    except (ValueError, TypeError):
                        continue
        
        # Sort by profit potential
        opportunities.sort(key=lambda x: x[4], reverse=True)  # Sort by profit
        
        # Save to sheets
        if opportunities:
            self.opportunities_sheet.clear()
            self.opportunities_sheet.update('A1:G1', [['Buy Location', 'Buy Price', 'Sell Location', 'Sell Price', 'Net Profit', 'Risk Score', 'Timestamp']])
            self.opportunities_sheet.append_rows(opportunities[:10])  # Top 10 opportunities
        
        return opportunities

    def calculate_risk_score(self, buy_location_data, sell_location_data, profit_margin):
        """Calculate risk score for an arbitrage opportunity"""
        base_risk = 0.1
        
        # High profit margins might indicate unstable prices
        if profit_margin > 50:
            base_risk += 0.3
        
        # Volume availability risk
        buy_volume = int(buy_location_data.get('Volume', 0))
        if buy_volume < 500:
            base_risk += 0.2
        
        # Weather/drought risk
        buy_weather = self.get_weather_impact(buy_location_data['Location'])
        sell_weather = self.get_weather_impact(sell_location_data['Location'])
        
        avg_drought_risk = (buy_weather['drought_risk'] + sell_weather['drought_risk']) / 2
        base_risk += avg_drought_risk * 0.3
        
        return min(base_risk, 1.0)  # Cap at 100%

    def estimate_transport_cost(self, from_location, to_location):
        """Estimate transportation costs between locations"""
        # Mock transportation cost matrix ($/unit)
        transport_matrix = {
            ('Central Valley', 'Bay Area'): 25,
            ('Central Valley', 'Southern CA'): 35,
            ('Imperial Valley', 'Southern CA'): 20,
            ('Imperial Valley', 'Bay Area'): 45,
            ('Sacramento Valley', 'Bay Area'): 30,
            ('Sacramento Valley', 'Southern CA'): 40,
        }
        
        # Try both directions
        cost = transport_matrix.get((from_location, to_location)) or \
               transport_matrix.get((to_location, from_location)) or 30  # Default cost
        
        return cost

    def update_dashboard(self):
        """Update dashboard with key metrics"""
        print("📊 Updating dashboard...")
        
        # Get current data
        all_data = self.rawdata_sheet.get_all_records()
        opportunities = self.opportunities_sheet.get_all_records()
        
        if all_data:
            df = pd.DataFrame(all_data)
            
            # Calculate key metrics
            metrics = [
                ['Metric', 'Value'],
                ['Active Markets', len(df['Location'].unique())],
                ['Average Price', f"${df['Price'].astype(float).mean():.0f}"],
                ['Price Spread', f"${df['Price'].astype(float).max() - df['Price'].astype(float).min():.0f}"],
                ['Total Volume', f"{df['Volume'].astype(int).sum():,}"],
                ['Active Opportunities', len(opportunities)],
                ['Last Updated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            ]
            
            # Update dashboard sheet
            self.dashboard_sheet.clear()
            self.dashboard_sheet.update('A1:B7', metrics)
            
            # Add top opportunity if available
            if opportunities:
                top_opp = opportunities[0]
                self.dashboard_sheet.update('D1:E6', [
                    ['Top Opportunity', ''],
                    ['Buy', f"{top_opp['Buy Location']} @ ${top_opp['Buy Price']}"],
                    ['Sell', f"{top_opp['Sell Location']} @ ${top_opp['Sell Price']}"],
                    ['Profit', f"${top_opp['Net Profit']}/unit"],
                    ['Risk', f"{float(top_opp['Risk Score'])*100:.0f}%"],
                    ['Updated', top_opp['Timestamp']]
                ])

    def run_full_cycle(self):
        """Run the complete arbitrage detection cycle"""
        print("\n" + "="*50)
        print("🌊 WATER ARBITRAGE SYSTEM - FULL CYCLE")
        print("="*50)
        
        start_time = datetime.now()
        
        try:
            # 1. Collect fresh market data
            water_data = self.collect_water_data()
            
            # 2. Run AI analysis
            ai_analysis = self.analyze_with_ai()
            
            # 3. Detect arbitrage opportunities
            opportunities = self.detect_arbitrage_opportunities()
            
            # 4. Update dashboard
            self.update_dashboard()
            
            # 5. Generate summary report
            self.generate_report(ai_analysis, opportunities, water_data)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            print(f"✅ Full cycle completed in {processing_time:.1f} seconds")
            print(f"📊 Data points collected: {len(water_data)}")
            print(f"🎯 Opportunities found: {len(opportunities)}")
            print(f"📈 Check your Google Sheet for detailed results!")
            
            return {
                'success': True,
                'data_points': len(water_data),
                'opportunities': len(opportunities),
                'processing_time': processing_time,
                'ai_analysis': ai_analysis
            }
            
        except Exception as e:
            error_msg = f"❌ Error in full cycle: {str(e)}"
            print(error_msg)
            return {'success': False, 'error': error_msg}

    def generate_report(self, ai_analysis, opportunities, water_data):
        """Generate a summary report"""
        print(f"\n📅 REPORT GENERATED: {datetime.now()}")
        print(f"💧 Markets Monitored: {len(set([item[0] for item in water_data]))}")
        print(f"🎯 Opportunities Found: {len(opportunities)}")
        
        if opportunities:
            best_opp = opportunities[0]
            print(f"\n💰 BEST OPPORTUNITY:")
            print(f"   Buy: {best_opp[0]} @ ${best_opp[1]}")
            print(f"   Sell: {best_opp[2]} @ ${best_opp[3]}")
            print(f"   Net Profit: ${best_opp[4]} per unit")
            print(f"   Risk Score: {float(best_opp[5])*100:.0f}%")
        
        print(f"\n🤖 AI INSIGHTS:")
        # Show first 200 characters of AI analysis
        print(ai_analysis[:200] + "..." if len(ai_analysis) > 200 else ai_analysis)

# Demo runner function
def run_demo():
    """Run a complete demo of the system"""
    print("🚀 Starting Water Arbitrage System Demo...")
    print("⚠️  Make sure you have:")
    print("   - Google Sheets API credentials.json file")
    print("   - .env file with OPENAI_API_KEY and GOOGLE_SHEET_URL")
    
    try:
        # Initialize system with environment variables
        system = WaterArbitrageSystem()
        
        # Run full cycle
        results = system.run_full_cycle()
        
        if results['success']:
            print("\n🎉 DEMO COMPLETED SUCCESSFULLY!")
            print("🔗 Check your Google Sheet for live results")
            print("⏱️  Set up a cron job to run this every hour for live monitoring")
        else:
            print(f"❌ Demo failed: {results['error']}")
            
    except Exception as e:
        print(f"❌ Demo setup failed: {str(e)}")
        print("💡 Make sure your credentials.json and API keys are configured correctly")

if __name__ == "__main__":
    run_demo()

# Additional utility functions for extended functionality
def setup_automated_runs():
    """Setup instructions for automated execution"""
    instructions = """
    🔄 TO SETUP AUTOMATED RUNS:
    
    1. Deploy this script to a cloud service (Google Cloud Functions, AWS Lambda, etc.)
    2. Set up a cron job to run every hour:
       
       Linux/Mac cron:
       0 * * * * /usr/bin/python3 /path/to/water_arbitrage.py
       
       Or use GitHub Actions with scheduled workflows
       
    3. Set environment variables for your API keys:
       export OPENAI_API_KEY="your_key_here"
       export GOOGLE_SHEET_URL="your_sheet_url_here"
    
    4. Monitor the Google Sheet for real-time updates
    """
    print(instructions)

def create_advanced_dashboard():
    """Instructions for creating advanced visualization"""
    instructions = """
    📊 ADVANCED DASHBOARD SETUP:
    
    1. In your Google Sheet, create charts:
       - Line chart for price trends over time
       - Bar chart comparing current prices by location
       - Scatter plot of profit vs risk for opportunities
    
    2. Add conditional formatting:
       - Green for profitable opportunities
       - Red for high-risk trades
       - Yellow for moderate opportunities
    
    3. Create data validation dropdowns for filtering
    
    4. Set up email alerts using Google Apps Script triggers
    """
    print(instructions)