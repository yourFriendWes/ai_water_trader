#!/usr/bin/env python3
"""
Veles Water Report Agent for Water Arbitrage System
Downloads and analyzes Veles Water weekly reports for market intelligence
"""

import os
import requests
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from openai import OpenAI
from bs4 import BeautifulSoup
import pdfplumber
import base64
from urllib.parse import urljoin, urlparse
import io

load_dotenv()

class VelesReportAgent:
    """Agent for analyzing Veles Water weekly reports"""
    
    def __init__(self):
        """Initialize the Veles report agent"""
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = os.getenv('VELES_AGENT_MODEL', 'gpt-4o')
        
        # Veles Water URLs
        self.base_url = "https://veleswater.com"
        self.reports_url = "https://veleswater.com/veleswater-weekly-report/"
        self.archive_url = "https://veleswater.com/veleswater-weekly-report-archive/"
        
        # Session for requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def find_latest_report(self) -> Dict[str, Any]:
        """
        Find the latest Veles Water report from both main page and archive
        
        Returns:
            Dict with report info including URL, date, and filename
        """
        print("🔍 Searching for latest Veles Water report...")
        
        try:
            # Check main reports page first
            main_reports = self._get_reports_from_page(self.reports_url)
            print(f"Found {len(main_reports)} reports on main page")
            
            # Check archive page
            archive_reports = self._get_reports_from_page(self.archive_url)
            print(f"Found {len(archive_reports)} reports in archive")
            
            # Combine and find latest
            all_reports = main_reports + archive_reports
            
            if not all_reports:
                return {
                    'success': False,
                    'error': 'No reports found on either page'
                }
            
            # Sort by date (most recent first)
            latest_report = max(all_reports, key=lambda x: x.get('date', datetime.min))
            
            print(f"✅ Latest report found: {latest_report.get('filename', 'Unknown')} from {latest_report.get('date', 'Unknown date')}")
            
            return {
                'success': True,
                'report': latest_report
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to find latest report: {str(e)}"
            }
    
    def _get_reports_from_page(self, url: str) -> List[Dict[str, Any]]:
        """Extract PDF report links from a Veles Water page"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            reports = []
            
            # Look for PDF links
            pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.I))
            
            for link in pdf_links:
                href = link.get('href')
                if not href:
                    continue
                
                # Make absolute URL
                pdf_url = urljoin(self.base_url, href)
                
                # Extract filename and try to parse date
                filename = os.path.basename(urlparse(pdf_url).path)
                
                # Try to extract date from filename or link text
                report_date = self._extract_date_from_text(filename + " " + link.get_text())
                
                reports.append({
                    'url': pdf_url,
                    'filename': filename,
                    'date': report_date,
                    'link_text': link.get_text().strip()
                })
            
            return reports
            
        except Exception as e:
            print(f"Error getting reports from {url}: {str(e)}")
            return []
    
    def _extract_date_from_text(self, text: str) -> datetime:
        """Extract date from filename or link text"""
        # Common date patterns in Veles reports
        date_patterns = [
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
            r'(\d{1,2})-(\d{1,2})-(\d{4})',  # MM-DD-YYYY
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
            r'(\w+)\s+(\d{1,2}),?\s+(\d{4})', # Month DD, YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                try:
                    groups = match.groups()
                    if len(groups) == 3:
                        if pattern == r'(\w+)\s+(\d{1,2}),?\s+(\d{4})':
                            # Month name format
                            month_str, day_str, year_str = groups
                            return datetime.strptime(f"{month_str} {day_str} {year_str}", "%B %d %Y")
                        elif pattern in [r'(\d{4})-(\d{1,2})-(\d{1,2})']:
                            # YYYY-MM-DD
                            year, month, day = map(int, groups)
                            return datetime(year, month, day)
                        else:
                            # MM-DD-YYYY or MM/DD/YYYY
                            month, day, year = map(int, groups)
                            return datetime(year, month, day)
                except (ValueError, TypeError):
                    continue
        
        # Default to current date if no date found
        return datetime.now()
    
    def download_pdf(self, pdf_url: str) -> Dict[str, Any]:
        """Download PDF report"""
        try:
            print(f"📥 Downloading PDF from {pdf_url}")
            
            response = self.session.get(pdf_url, timeout=60)
            response.raise_for_status()
            
            return {
                'success': True,
                'content': response.content,
                'size': len(response.content),
                'url': pdf_url
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to download PDF: {str(e)}"
            }
    
    def extract_pdf_data(self, pdf_content: bytes) -> Dict[str, Any]:
        """Extract text and images from PDF using pdfplumber"""
        try:
            extracted_data = {
                'text': '',
                'tables': [],
                'images': [],
                'pages': 0
            }
            
            with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                extracted_data['pages'] = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages):
                    # Extract text
                    page_text = page.extract_text() or ""
                    extracted_data['text'] += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                    
                    # Extract tables
                    tables = page.extract_tables()
                    for table in tables:
                        if table:
                            extracted_data['tables'].append({
                                'page': page_num + 1,
                                'data': table
                            })
                    
                    # Note: pdfplumber doesn't directly extract images
                    # For images, you'd need additional libraries like PyMuPDF
            
            return {
                'success': True,
                'data': extracted_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to extract PDF data: {str(e)}"
            }
    
    def analyze_pdf_with_ai(self, pdf_content: bytes, pdf_url: str) -> str:
        """Extract PDF content and have AI analyze it"""
        
        # First extract text from PDF
        extract_result = self.extract_pdf_data(pdf_content)
        if not extract_result['success']:
            return f"❌ **PDF Extraction Failed**\n\nError: {extract_result['error']}\n\n🔗 **Source**: {pdf_url}"
        
        pdf_data = extract_result['data']
        
        # Prepare text content for AI analysis (limit to avoid token limits)
        text_content = pdf_data['text'][:15000]  # Limit to ~15k characters
        
        # Prepare tables text
        tables_text = ""
        for i, table in enumerate(pdf_data['tables'][:3]):  # Limit to first 3 tables
            tables_text += f"\n--- Table {i+1} (Page {table['page']}) ---\n"
            for row in table['data'][:10]:  # Limit to first 10 rows per table
                if row:  # Check if row is not empty
                    tables_text += " | ".join([str(cell) if cell else "" for cell in row]) + "\n"
        
        prompt = f"""
Task: Analyze this Veles Water weekly report content and extract key information.

PDF TEXT CONTENT:
{text_content}

TABLES FOUND:
{tables_text[:5000]}

Please extract and format the following information:

📄 **Report Summary**
- Report date (look for dates in the content)
- NQH₂O spot index price (if available)  
- Week-over-week % change
- Key highlights (2-3 bullet points)

📊 **Water Prices & Futures** (format as markdown table)
- Current spot prices
- Futures spreads  
- Any price changes mentioned

🌧️ **Weather & Drought Summary**
- Precipitation levels mentioned
- Snowpack conditions  
- Reservoir storage stats
- Weather outlook
- Drought conditions

🔗 **Source**
PDF Link: {pdf_url}

Format the response in clean Markdown. If specific data points aren't found, note "Data not available in this report."

Focus on water market pricing, weather impacts, and drought conditions. Be concise but comprehensive.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a water market analyst extracting key information from Veles Water reports. Focus on pricing data, weather impacts, and market conditions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"❌ **AI Analysis Failed**\n\nError: {str(e)}\n\n🔗 **Source**: {pdf_url}"
    
    def get_drought_monitor_map(self) -> Optional[str]:
        """Get latest U.S. Drought Monitor map as fallback"""
        try:
            # U.S. Drought Monitor current map URL
            drought_map_url = "https://droughtmonitor.unl.edu/data/png/current/current_usdm.png"
            
            response = self.session.get(drought_map_url, timeout=30)
            if response.status_code == 200:
                # Encode image as base64 for embedding
                img_b64 = base64.b64encode(response.content).decode()
                return f"data:image/png;base64,{img_b64}"
            
        except Exception as e:
            print(f"Failed to get drought monitor map: {str(e)}")
        
        return None
    
    def run_analysis(self) -> str:
        """
        Complete workflow: find latest report, download, extract, and analyze
        """
        print("🚀 Starting Veles Water report analysis...")
        
        # Step 1: Find latest report
        report_result = self.find_latest_report()
        if not report_result['success']:
            return f"❌ **Error**: {report_result['error']}"
        
        report_info = report_result['report']
        print(f"✅ Found latest report: {report_info['filename']}")
        
        # Step 2: Download PDF content
        print("📥 Downloading PDF...")
        download_result = self.download_pdf(report_info['url'])
        if not download_result['success']:
            return f"❌ **Download Error**: {download_result['error']}"
        
        print(f"✅ Downloaded PDF: {download_result['size']} bytes")
        
        # Step 3: AI Analysis of PDF content
        print("🤖 Running AI analysis on PDF content...")
        analysis = self.analyze_pdf_with_ai(download_result['content'], report_info['url'])
        
        # Step 4: Add drought map if needed
        drought_map = self.get_drought_monitor_map()
        if drought_map:
            analysis += f"\n\n🗺️ **Latest U.S. Drought Monitor Map**\n\n![Drought Monitor]({drought_map})\n\n*Source: U.S. Drought Monitor*"
        
        print("✅ Analysis complete!")
        return analysis

def main():
    """Test the Veles report agent"""
    try:
        agent = VelesReportAgent()
        result = agent.run_analysis()
        print("\n" + "="*80)
        print("VELES WATER REPORT ANALYSIS")
        print("="*80)
        print(result)
        
    except Exception as e:
        print(f"❌ Agent failed: {str(e)}")

if __name__ == "__main__":
    main()