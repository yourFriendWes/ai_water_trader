#!/usr/bin/env python3
"""
API Driver for Water Arbitrage System
Handles calls to various external APIs with authentication
"""

import requests
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import json

load_dotenv()

class APIDriver:
    def __init__(self):
        """Initialize API driver with environment variables"""
        self.ncdc_api_key = os.getenv('NCDC_API_KEY')
        self.session = requests.Session()
        
    def call_noaa_water_monitor(self) -> Dict[str, Any]:
        """
        Call NOAA water monitoring API
        Equivalent to: curl -X 'GET' 'https://api.water.noaa.gov/nwps/v1/monitor' -H 'accept: application/json'
        """
        url = "https://api.water.noaa.gov/nwps/v1/monitor"
        headers = {
            'accept': 'application/json'
        }
        
        if self.ncdc_api_key:
            headers['Authorization'] = f'Bearer {self.ncdc_api_key}'
        
        try:
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json(),
                'status_code': response.status_code
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def call_api_with_auth(self, url: str, method: str = 'GET', 
                          auth_header: Optional[str] = None, 
                          api_key: Optional[str] = None,
                          headers: Optional[Dict[str, str]] = None,
                          params: Optional[Dict[str, Any]] = None,
                          data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generic API caller with authentication support
        
        Args:
            url: API endpoint URL
            method: HTTP method (GET, POST, etc.)
            auth_header: Custom authorization header value
            api_key: API key to use (defaults to NCDC_API_KEY)
            headers: Additional headers
            params: Query parameters
            data: Request body data
        """
        request_headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        if headers:
            request_headers.update(headers)
            
        # Add authentication
        if auth_header:
            request_headers['Authorization'] = auth_header
        elif api_key or self.ncdc_api_key:
            key = api_key or self.ncdc_api_key
            request_headers['Authorization'] = f'Bearer {key}'
        
        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                headers=request_headers,
                params=params,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            # Try to parse JSON, fallback to text
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = response.text
            
            return {
                'success': True,
                'data': response_data,
                'status_code': response.status_code,
                'headers': dict(response.headers)
            }
            
        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            status_code = None
            
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text or str(e)
            
            return {
                'success': False,
                'error': error_detail,
                'status_code': status_code
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test API connection with a simple call"""
        return self.call_noaa_water_monitor()