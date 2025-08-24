"""Tushare API client for fetching stock data."""

import tushare as ts
from config import TUSHARE_TOKEN

class TushareClient:
    """A wrapper class for the Tushare Pro API."""

    def __init__(self):
        """Initialize the Tushare Pro API client."""
        ts.set_token(TUSHARE_TOKEN)
        self.pro = ts.pro_api()
        print("--- Tushare Pro API initialized successfully ---")

    def get_daily_data(self, ts_code, start_date, end_date):
        """
        Fetch daily stock price data for a given stock code and date range.

        Args:
            ts_code (str): The stock code (e.g., '601818.SH').
            start_date (str): The start date in 'YYYYMMDD' format.
            end_date (str): The end date in 'YYYYMMDD' format.

        Returns:
            pandas.DataFrame: A DataFrame containing the daily price data.
        """
        try:
            df_daily = self.pro.daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                fields='ts_code,trade_date,open,high,low,close,vol,amount'
            )
            return df_daily
        except Exception as e:
            print(f"Error fetching daily data: {e}")
            return None