"""Data fetcher that orchestrates the process of getting and storing stock data from both Tushare and Ashare APIs."""

import datetime
import pandas as pd
from api.tushare_client import TushareClient
from api.ashare_client import AshareClient
from database.db_manager import DatabaseManager
from utils.indicator_calculator import IndicatorCalculator
from utils.code_converter import convert_tushare_to_ashare_code
from config import DEFAULT_STOCK_CODE, DEFAULT_DAYS_BACK


class TushareDataFetcher:
    """Handles data fetching and storing for Tushare API."""
    
    def __init__(self, db_manager):
        """Initialize with database manager."""
        self.client = TushareClient()
        self.db_manager = db_manager
    
    def fetch_and_store(self, stock_code=DEFAULT_STOCK_CODE, days_back=DEFAULT_DAYS_BACK):
        """
        Fetch and store daily stock data for a given stock code using Tushare API.

        Args:
            stock_code (str): The stock code to fetch data for.
            days_back (int): The number of days back to fetch data from today.
        """
        # Set query date range
        end_date = datetime.date.today().strftime('%Y%m%d')
        start_date = (datetime.date.today() - datetime.timedelta(days=days_back)).strftime('%Y%m%d')

        print(f"\n--- Fetching daily historical price data for {stock_code} using Tushare ---")
        table_name = 'daily_price_tushare'

        # Check if data already exists in the database
        if not self.db_manager.check_data_exists(table_name, stock_code, start_date, end_date):
            print(f"Data for {stock_code} from {start_date} to {end_date} not found in {table_name} table. Fetching from API...")
            try:
                # Call API to get daily price data
                df_daily = self.client.get_daily_data(stock_code, start_date, end_date)

                if df_daily is not None and not df_daily.empty:
                    print(f"Successfully fetched {len(df_daily)} daily records for {stock_code}.")
                    print("Data preview (latest 5 records):")
                    print(df_daily.head())
                    
                    # Save data to database
                    self.db_manager.save_daily_price_data(df_daily, source='tushare')
                    
                    # Calculate indicators
                    print("Calculating technical indicators...")
                    indicator_calculator = IndicatorCalculator(df_daily)
                    df_indicators = indicator_calculator.calculate_all_indicators()
                    
                    # Save indicators to database
                    self.db_manager.save_indicators_data(df_indicators, source='tushare')
                    print("Technical indicators calculated and saved.")
                else:
                    print(f"Failed to fetch data for {stock_code}. Please check the stock code or date range.")

            except Exception as e:
                print(f"Error occurred while fetching data: {e}")
        else:
            print(f"Data for {stock_code} from {start_date} to {end_date} already exists in {table_name} table. Skipping API call.")


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


class StockDataFetcher:
    """Orchestrates the fetching and storing of stock data."""
    
    def __init__(self):
        """Initialize the fetcher with API clients and database manager."""
        self.db_manager = DatabaseManager()
        self.tushare_fetcher = TushareDataFetcher(self.db_manager)
        self.ashare_fetcher = AshareDataFetcher(self.db_manager)

    def fetch_and_store_data_tushare(self, stock_code=DEFAULT_STOCK_CODE, days_back=DEFAULT_DAYS_BACK):
        """
        Fetch and store daily stock data for a given stock code using Tushare API.

        Args:
            stock_code (str): The stock code to fetch data for.
            days_back (int): The number of days back to fetch data from today.
        """
        self.tushare_fetcher.fetch_and_store(stock_code, days_back)

    def fetch_and_store_data_ashare(self, stock_code, days_back=DEFAULT_DAYS_BACK):
        """
        Fetch and store daily stock data for a given stock code using Ashare API.

        Args:
            stock_code (str): The stock code to fetch data for (e.g., '601818').
            days_back (int): The number of days back to fetch data from today.
        """
        self.ashare_fetcher.fetch_and_store(stock_code, days_back)