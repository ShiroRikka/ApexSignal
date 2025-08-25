"""Data fetcher that orchestrates the process of getting and storing stock data from Tushare API."""

import datetime
import pandas as pd
from api.tushare_client import TushareClient
from database.db_manager import DatabaseManager
from utils.indicator_calculator import IndicatorCalculator
from config import DEFAULT_STOCK_CODE, DEFAULT_DAYS_BACK
from data.data_fetcher_base import DataFetcher


class TushareDataFetcher(DataFetcher):
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