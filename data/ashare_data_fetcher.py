"""Data fetcher that orchestrates the process of getting and storing stock data using Ashare API."""

import datetime
import pandas as pd
from api.ashare_client import AshareClient
from database.db_manager import DatabaseManager
from utils.indicator_calculator import IndicatorCalculator
from utils.code_converter import convert_tushare_to_ashare_code
from config import DEFAULT_STOCK_CODE, DEFAULT_DAYS_BACK

class AshareDataFetcher:
    """Orchestrates the fetching and storing of stock data using Ashare API."""

    def __init__(self):
        """Initialize the fetcher with API client and database manager."""
        self.ashare_client = AshareClient()
        self.db_manager = DatabaseManager()

    def fetch_and_store_data(self, stock_code=DEFAULT_STOCK_CODE, days_back=DEFAULT_DAYS_BACK):
        """
        Fetch and store daily stock data for a given stock code using Ashare API.

        Args:
            stock_code (str): The stock code to fetch data for.
            days_back (int): The number of days back to fetch data from today.
        """
        print(f"\n--- Fetching daily historical price data for {stock_code} using Ashare API ---")

        # Convert stock code format if needed (from Tushare to Ashare)
        ashare_code = convert_tushare_to_ashare_code(stock_code)

        # Check if data already exists in the database
        end_date = datetime.date.today().strftime('%Y%m%d')
        start_date = (datetime.date.today() - datetime.timedelta(days=days_back)).strftime('%Y%m%d')
        
        if not self.db_manager.check_data_exists('daily_price', stock_code, start_date, end_date):
            print(f"Data for {stock_code} from {start_date} to {end_date} not found in database. Fetching from Ashare API...")
            try:
                # Call Ashare API to get daily price data
                df_daily = self.ashare_client.get_price(
                    code=ashare_code, 
                    frequency='1d', 
                    count=days_back
                )

                if df_daily is not None and not df_daily.empty:
                    print(f"Successfully fetched {len(df_daily)} daily records for {stock_code}.")
                    print("Data preview (latest 5 records):")
                    print(df_daily.head())
                    
                    # Process and format the data to match our database schema
                    # Note: This is a simplified implementation. In a real scenario,
                    # you would need to properly map Ashare data to your schema.
                    df_daily['ts_code'] = stock_code
                    df_daily['trade_date'] = df_daily.index.strftime('%Y%m%d')
                    df_daily['vol'] = df_daily['volume']
                    df_daily['amount'] = 0  # Ashare may not provide amount data
                    
                    # Reorder columns to match database schema
                    df_daily = df_daily[['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount']]
                    
                    # Save data to database
                    self.db_manager.save_daily_price_data(df_daily)
                    
                    # Calculate indicators
                    print("Calculating technical indicators...")
                    indicator_calculator = IndicatorCalculator(df_daily)
                    df_indicators = indicator_calculator.calculate_all_indicators()
                    
                    # Save indicators to database
                    self.db_manager.save_indicators_data(df_indicators)
                    print("Technical indicators calculated and saved.")
                else:
                    print(f"Failed to fetch data for {stock_code}. Please check the stock code or date range.")

            except Exception as e:
                print(f"Error occurred while fetching data: {e}")
        else:
            print(f"Data for {stock_code} from {start_date} to {end_date} already exists in the database. Skipping API call.")