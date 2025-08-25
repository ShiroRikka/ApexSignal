"""Data fetcher that orchestrates the process of getting and storing stock data from Ashare API."""

import datetime
import pandas as pd
from api.ashare_client import AshareClient
from database.db_manager import DatabaseManager
from utils.indicator_calculator import IndicatorCalculator
from utils.code_converter import convert_tushare_to_ashare_code
from config import DEFAULT_STOCK_CODE, DEFAULT_DAYS_BACK


class AshareDataFetcher:
    """Handles data fetching and storing for Ashare API."""
    
    def __init__(self, db_manager):
        """Initialize with database manager."""
        self.client = AshareClient()
        self.db_manager = db_manager
    
    def fetch_and_store(self, stock_code, days_back=DEFAULT_DAYS_BACK):
        """
        Fetch and store daily stock data for a given stock code using Ashare API.

        Args:
            stock_code (str): The stock code to fetch data for (e.g., '601818').
            days_back (int): The number of days back to fetch data from today.
        """
        # Format stock code for Ashare (e.g., 'sh601818')
        formatted_code = convert_tushare_to_ashare_code(stock_code)
        table_name = 'daily_price_ashare'
        
        print(f"\n--- Fetching daily historical price data for {formatted_code} using Ashare ---")
        
        try:
            # Call Ashare API to get daily price data
            df_daily = self.client.get_price(code=formatted_code, frequency='1d', count=days_back)
            
            if df_daily is not None and not df_daily.empty:
                print(f"Successfully fetched {len(df_daily)} daily records for {formatted_code}.")
                print("Data preview (latest 5 records):")
                print(df_daily.head())
                
                # Add ts_code column to match database schema
                df_daily['ts_code'] = stock_code  # Store original code without 'sh'/'sz' prefix
                
                # Add trade_date column from index
                df_daily['trade_date'] = df_daily.index.strftime('%Y%m%d')
                
                # Rename columns to match database schema
                df_daily.rename(columns={
                    'open': 'open',
                    'high': 'high',
                    'low': 'low',
                    'close': 'close',
                    'volume': 'vol'
                }, inplace=True)
                
                # Add missing 'amount' column with default value 0.0
                df_daily['amount'] = 0.0
                
                # Reorder columns to match database schema
                expected_columns = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount']
                df_daily = df_daily[expected_columns]
                
                # Save data to database
                self.db_manager.save_daily_price_data(df_daily, source='ashare')
                
                # Calculate indicators
                print("Calculating technical indicators...")
                indicator_calculator = IndicatorCalculator(df_daily)
                df_indicators = indicator_calculator.calculate_all_indicators()
                
                # Save indicators to database
                self.db_manager.save_indicators_data(df_indicators, source='ashare')
                print("Technical indicators calculated and saved.")
            else:
                print(f"Failed to fetch data for {formatted_code}. Please check the stock code or date range.")

        except Exception as e:
            print(f"Error occurred while fetching data: {e}")