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
        Uses forward adjusted prices for accurate technical analysis.

        Args:
            ts_code (str): The stock code (e.g., '601818.SH').
            start_date (str): The start date in 'YYYYMMDD' format.
            end_date (str): The end date in 'YYYYMMDD' format.

        Returns:
            pandas.DataFrame: A DataFrame containing the daily price data.
        """
        try:
            # Using pro_bar interface which is more feature-rich
            df_daily = ts.pro_bar(
                ts_code=ts_code,
                adj='qfq',  # Use forward adjusted prices
                start_date=start_date,
                end_date=end_date,
                asset='E',  # E for stocks
                freq='D'   # Daily frequency
            )
            
            # Ensure we return the data with the expected columns
            if df_daily is not None and not df_daily.empty:
                # Reorder columns to match our expected format
                expected_columns = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount']
                # Check if all expected columns exist in the DataFrame
                missing_columns = set(expected_columns) - set(df_daily.columns)
                if not missing_columns:
                    df_daily = df_daily[expected_columns]
                else:
                    print(f"Warning: Missing columns in fetched data: {missing_columns}")
            
            return df_daily
        except Exception as e:
            print(f"Error fetching daily data: {e}")
            return None