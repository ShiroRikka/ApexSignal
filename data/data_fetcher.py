"""Data fetcher that orchestrates the process of getting and storing stock data."""

import datetime
from api.tushare_client import TushareClient
from database.db_manager import DatabaseManager
from config import DEFAULT_STOCK_CODE, DEFAULT_DAYS_BACK

class StockDataFetcher:
    """Orchestrates the fetching and storing of stock data."""

    def __init__(self):
        """Initialize the fetcher with API client and database manager."""
        self.tushare_client = TushareClient()
        self.db_manager = DatabaseManager()

    def fetch_and_store_data(self, stock_code=DEFAULT_STOCK_CODE, days_back=DEFAULT_DAYS_BACK):
        """
        Fetch and store daily stock data for a given stock code.

        Args:
            stock_code (str): The stock code to fetch data for.
            days_back (int): The number of days back to fetch data from today.
        """
        # Set query date range
        end_date = datetime.date.today().strftime('%Y%m%d')
        start_date = (datetime.date.today() - datetime.timedelta(days=days_back)).strftime('%Y%m%d')

        print(f"\n--- Fetching daily historical price data for {stock_code} ---")

        # Check if data already exists in the database
        if not self.db_manager.check_data_exists('daily_price', stock_code, start_date, end_date):
            print(f"Data for {stock_code} from {start_date} to {end_date} not found in database. Fetching from API...")
            try:
                # Call API to get daily price data
                df_daily = self.tushare_client.get_daily_data(stock_code, start_date, end_date)

                if df_daily is not None and not df_daily.empty:
                    print(f"Successfully fetched {len(df_daily)} daily records for {stock_code}.")
                    print("Data preview (latest 5 records):")
                    print(df_daily.head())
                    
                    # Save data to database
                    self.db_manager.save_daily_price_data(df_daily)
                else:
                    print(f"Failed to fetch data for {stock_code}. Please check the stock code or date range.")

            except Exception as e:
                print(f"Error occurred while fetching data: {e}")
        else:
            print(f"Data for {stock_code} from {start_date} to {end_date} already exists in the database. Skipping API call.")