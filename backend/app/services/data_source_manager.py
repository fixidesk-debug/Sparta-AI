"""
Data Source Manager - Manage Multiple Data Sources
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DataSourceManager:
    """Manage external data sources"""
    
    @staticmethod
    def fetch_from_api(
        url: str,
        method: str = 'GET',
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> pd.DataFrame:
        """Fetch data from REST API"""
        try:
            import requests
            
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            json_data = response.json()
            
            if isinstance(json_data, list):
                df = pd.DataFrame(json_data)
            elif isinstance(json_data, dict):
                if 'data' in json_data:
                    df = pd.DataFrame(json_data['data'])
                else:
                    df = pd.DataFrame([json_data])
            else:
                raise ValueError("Unsupported JSON format")
            
            return df
            
        except Exception as e:
            logger.error(f"API fetch error: {e}")
            raise
    
    @staticmethod
    def fetch_from_google_sheets(
        spreadsheet_id: str,
        sheet_name: str,
        credentials_json: Dict
    ) -> pd.DataFrame:
        """Fetch data from Google Sheets"""
        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
            
            creds = Credentials.from_service_account_info(credentials_json)
            service = build('sheets', 'v4', credentials=creds)
            
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=sheet_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return pd.DataFrame()
            
            df = pd.DataFrame(values[1:], columns=values[0])
            return df
            
        except Exception as e:
            logger.error(f"Google Sheets fetch error: {e}")
            raise
    
    @staticmethod
    def fetch_from_url(url: str) -> pd.DataFrame:
        """Fetch CSV/Excel from URL"""
        try:
            if url.endswith('.csv'):
                df = pd.read_csv(url)
            elif url.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(url)
            elif url.endswith('.json'):
                df = pd.read_json(url)
            else:
                raise ValueError("Unsupported file format")
            
            return df
            
        except Exception as e:
            logger.error(f"URL fetch error: {e}")
            raise
