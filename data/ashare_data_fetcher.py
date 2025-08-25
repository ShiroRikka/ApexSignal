"""Data fetcher that orchestrates the process of getting and storing stock data from Ashare API."""

import datetime
import pandas as pd
from api.ashare_client import AshareClient
from database.db_manager import DatabaseManager
from utils.indicator_calculator import IndicatorCalculator
from utils.code_converter import convert_tushare_to_ashare_code
from utils.ashare_data_processor import process_ashare_data  # Import the new utility function
from config import DEFAULT_STOCK_CODE, DEFAULT_DAYS_BACK
from data.data_fetcher_base import DataFetcher


class AshareDataFetcher(DataFetcher):
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
                
                # Process data using the utility function
                df_daily = process_ashare_data(df_daily, stock_code)
                
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