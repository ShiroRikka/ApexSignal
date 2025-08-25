"""Orchestrates the fetching and storing of stock data from multiple APIs."""

from database.db_manager import DatabaseManager
from data.tushare_data_fetcher import TushareDataFetcher
from data.ashare_data_fetcher import AshareDataFetcher
from config import DEFAULT_STOCK_CODE, DEFAULT_DAYS_BACK


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