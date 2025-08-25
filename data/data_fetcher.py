"""Orchestrates the fetching, storing, and viewing of stock data from multiple APIs."""

from database.db_manager import DatabaseManager
from data.tushare_data_fetcher import TushareDataFetcher
from data.ashare_data_fetcher import AshareDataFetcher
from config import DEFAULT_STOCK_CODE, DEFAULT_DAYS_BACK


class StockDataFetcher:
    """Orchestrates the fetching, storing, and viewing of stock data."""
    
    def __init__(self):
        """Initialize the fetcher with API clients and database manager."""
        self.db_manager = DatabaseManager()
        self.tushare_fetcher = TushareDataFetcher(self.db_manager)
        self.ashare_fetcher = AshareDataFetcher(self.db_manager)
        # Map source names to fetcher instances
        self.fetchers = {
            'tushare': self.tushare_fetcher,
            'ashare': self.ashare_fetcher
        }

    def fetch_and_store_data(self, source, stock_code=DEFAULT_STOCK_CODE, days_back=DEFAULT_DAYS_BACK):
        """
        Fetch and store daily stock data for a given stock code using the specified API.

        Args:
            source (str): Data source ('tushare' or 'ashare').
            stock_code (str): The stock code to fetch data for.
            days_back (int): The number of days back to fetch data from today.
        """
        if source in self.fetchers:
            self.fetchers[source].fetch_and_store(stock_code, days_back)
        else:
            print(f"Unsupported data source: {source}")

    def fetch_and_store_data_tushare(self, stock_code=DEFAULT_STOCK_CODE, days_back=DEFAULT_DAYS_BACK):
        """
        Fetch and store daily stock data for a given stock code using Tushare API.

        Args:
            stock_code (str): The stock code to fetch data for.
            days_back (int): The number of days back to fetch data from today.
        """
        self.fetch_and_store_data('tushare', stock_code, days_back)

    def fetch_and_store_data_ashare(self, stock_code, days_back=DEFAULT_DAYS_BACK):
        """
        Fetch and store daily stock data for a given stock code using Ashare API.

        Args:
            stock_code (str): The stock code to fetch data for (e.g., '601818').
            days_back (int): The number of days back to fetch data from today.
        """
        # For Ashare, we expect a simpler stock code format like '601818'
        formatted_stock_code = stock_code.split('.')[0] if '.' in stock_code else stock_code
        self.fetch_and_store_data('ashare', formatted_stock_code, days_back)
        
    def view_latest_data(self, source, stock_code, limit=5):
        """
        View the latest data records for a specific stock.

        Args:
            source (str): Data source ('tushare' or 'ashare').
            stock_code (str): The stock code.
            limit (int): The number of latest records to retrieve.
        """
        # Validate source
        if source not in self.db_manager.get_supported_sources():
            print(f"Unsupported data source: {source}")
            return
            
        # For viewing, we need to use the correct stock code format for each source
        formatted_stock_code = stock_code if source == 'tushare' else stock_code.split('.')[0]
        
        print(f"\n--- Latest Daily Price Data from {source} ---")
        daily_records = self.db_manager.get_latest_data('daily_price', source, formatted_stock_code, limit)
        if daily_records:
            for record in daily_records:
                print(record)
        else:
            print("No daily price data found for the specified stock code.")
            
        print(f"\n--- Latest Indicators Data from {source} ---")
        indicator_records = self.db_manager.get_latest_data('indicators', source, formatted_stock_code, limit)
        if indicator_records:
            for record in indicator_records:
                print(record)
        else:
            print("No indicators data found for the specified stock code.")
