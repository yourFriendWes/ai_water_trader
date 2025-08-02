# 🌊 AI Water Trader

An intelligent water arbitrage system that combines multiple data sources and AI analysis to identify profitable water trading opportunities. Built for the evolving water markets in California and beyond.

## 🚀 Features

### Core System
- **Water Arbitrage Analysis**: AI-powered identification of buy/sell opportunities across different water markets
- **Multi-Source Data Integration**: Combines climate intelligence, market reports, and real-time data
- **Google Sheets Dashboard**: Live data tracking and analysis results
- **Automated Trading Signals**: AI-generated recommendations with risk assessment

### Data Sources & Agents

#### 1. **Climate News Agent** (`climate_news_agent.py`)
- Monitors climate events affecting water supply/demand
- Searches for drought, wildfire, precipitation, and weather pattern news
- Provides structured climate intelligence for trading decisions

#### 2. **Veles Water Report Agent** (`veles_report_agent.py`)
- Downloads and analyzes latest Veles Water weekly reports
- Extracts NQH₂O index prices, futures spreads, and market trends
- Processes weather conditions, reservoir levels, and drought status

#### 3. **NASDAQ Data Agent** (`nasdaq_data_agent.py`)
- Downloads historical water index data from NASDAQ
- Uploads structured data to Google Sheets for analysis
- Tracks water commodity price movements

#### 4. **API Driver** (`api_driver.py`)
- Unified interface for external API calls (NOAA, Polygon, FRED)
- Handles authentication and rate limiting
- Supports multiple data providers

## 📊 Sample Output

### Climate Intelligence (Structured)
```json
{
    "timestamp": "2025-08-01T18:30:00Z",
    "agent_type": "climate_events",
    "events": [
        {
            "event_type": "drought",
            "location": "Central Valley, CA",
            "severity": 8,
            "operational_impact": "high",
            "timeline": "immediate",
            "details": "Exceptional drought conditions affecting 2.3M acres",
            "recommended_actions": ["increase_water_reserves", "monitor_prices"]
        }
    ],
    "summary": "Severe drought conditions driving water scarcity across key agricultural regions"
}
```

### Veles Water Report Intelligence (Structured)
```json
{
    "timestamp": "2025-08-01T18:30:00Z",
    "agent_type": "veles_water_report",
    "report_date": "2025-05-22",
    "water_market": {
        "nqh2o_index": {
            "spot_price": 341.73,
            "week_change_percent": -3.93,
            "price_currency": "USD"
        },
        "futures": [
            {
                "contract": "June 2025",
                "price": 345.0,
                "spread_to_index": -6.72
            }
        ]
    },
    "weather_conditions": {
        "precipitation": {
            "central_valley": 0.37,
            "percent_of_average": 88
        },
        "snowpack": {
            "water_equivalent": 4.5,
            "percent_of_average": 67
        }
    },
    "reservoir_storage": [
        {
            "name": "Lake Oroville",
            "capacity_percent": 99,
            "historical_percent": 122
        }
    ],
    "key_insights": [
        "NQH2O index decreased $13.99 from previous week",
        "Futures trading at discount to spot index",
        "Reservoir levels above historical average despite drought"
    ]
}
```

### AI Trading Analysis (Human-Readable)
```
🤖 AI WATER ARBITRAGE ANALYSIS

**Top 3 Arbitrage Opportunities:**
1. Central Valley → Southern CA: Buy at $341.73, Sell at $385.50 (+12.8% margin)
2. Imperial Valley → Bay Area: Spread opportunity worth $28/acre-foot
3. Futures Arbitrage: June contracts trading $6.72 below spot index

**Climate-Adjusted Risk Factors:**
- Exceptional drought conditions increase demand volatility
- Snowpack at 67% of average reduces spring supply expectations
- Weather outlook shows continued dry conditions through Q3

**Optimal Timing:** Execute within 48 hours before weekend weather reports

**Expected Profit Margins:** 8-15% after transaction costs and climate risk premiums
```

## 🛠️ Installation & Setup

### Prerequisites
```bash
pip install pandas gspread oauth2client openai python-dotenv requests beautifulsoup4 pdfplumber
```

### Environment Variables
Create `.env` file:
```bash
GOOGLE_SHEET_URL="your_google_sheet_url"
OPENAI_API_KEY="your_openai_api_key"
NCDC_API_KEY="your_noaa_api_key"
POLYGON_API_KEY="your_polygon_api_key"
FRED_API_KEY="your_fred_api_key"
```

### Google Sheets Setup
1. Create Google Cloud Project and enable Sheets API
2. Download `credentials.json` service account file
3. Share your Google Sheet with the service account email
4. Update `GOOGLE_SHEET_URL` in `.env`

## 🚀 Usage

### Run Full Analysis
```bash
python water_arbitrage_system.py
```

### Individual Agents
```python
# Climate Intelligence
from climate_news_agent import ClimateNewsAgent
climate_agent = ClimateNewsAgent()
climate_data = climate_agent.get_climate_intelligence_safe(format='structured')

# Veles Water Reports
from veles_report_agent import VelesReportAgent
veles_agent = VelesReportAgent()
market_data = veles_agent.get_veles_intelligence(format='structured')

# NASDAQ Data
from nasdaq_data_agent import NASDAQDataAgent
nasdaq_agent = NASDAQDataAgent()
nasdaq_agent.download_and_upload("NQH2O")
```

## 📈 Dashboard

The system creates a live Google Sheets dashboard with tabs:
- **Raw Data**: Market transactions and pricing data
- **AI Analysis**: Trading recommendations and risk assessments
- **Climate Intel**: Weather events and climate intelligence
- **NASDAQ Data**: Historical price movements and trends

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Climate News   │    │  Veles Reports  │    │  NASDAQ Data    │
│     Agent       │    │     Agent       │    │     Agent       │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────┬───────────────────────────────┘
                         │
                ┌─────────▼─────────┐
                │  Water Arbitrage  │
                │      System       │
                └─────────┬─────────┘
                          │
                ┌─────────▼─────────┐
                │  Google Sheets    │
                │    Dashboard      │
                └───────────────────┘
```

## 🔧 API Integrations

- **OpenAI GPT-4**: Market analysis and trading signal generation
- **NOAA APIs**: Weather and climate data
- **Veles Water**: Weekly market reports and analysis
- **NASDAQ**: Historical water index data
- **Polygon.io**: Real-time market data
- **FRED**: Economic indicators

## 📊 Data Flow

1. **Data Collection**: Agents gather data from multiple sources
2. **AI Processing**: OpenAI analyzes market conditions with climate context
3. **Signal Generation**: System identifies arbitrage opportunities
4. **Risk Assessment**: Climate intelligence adjusts risk factors
5. **Dashboard Update**: Results saved to Google Sheets for tracking

## 🌟 Key Innovations

- **Multi-Modal Intelligence**: Combines market data with climate events
- **Automated PDF Analysis**: Extracts structured data from water market reports
- **Real-Time Climate Integration**: Weather events influence trading decisions
- **Scalable Agent Architecture**: Easy to add new data sources
- **Cloud-Ready**: No local file dependencies, memory-only processing

## 🚨 Risk Considerations

- Water markets are highly regulated - ensure compliance
- Climate events can cause rapid price volatility
- Limited liquidity in some regional markets
- Physical delivery constraints affect arbitrage execution

## 📄 License

MIT License - See LICENSE file for details

---

**Built for SeaTech Week 2025** 🌊
*Leveraging AI to optimize water resource allocation in an era of climate change*