"""Main entry point for the stock data collector application."""

import argparse
import os
import sqlite3
from data.data_fetcher import StockDataFetcher
from config import DEFAULT_STOCK_CODE, DEFAULT_DAYS_BACK
from database.db_manager import DatabaseManager

def main():
    """Main function to parse arguments and initiate data fetching or viewing."""
    parser = argparse.ArgumentParser(description="Stock Data Collector")
    parser.add_argument(
        "--stock_code",
        type=str,
        default=DEFAULT_STOCK_CODE,
        help=f"Stock code to fetch data for (e.g., 000001.SZ). Default is {DEFAULT_STOCK_CODE}."
    )
    parser.add_argument(
        "--days_back",
        type=int,
        default=DEFAULT_DAYS_BACK,
        help=f"Number of days back to fetch data. Default is {DEFAULT_DAYS_BACK}."
    )
    parser.add_argument(
        "--source",
        type=str,
        choices=['tushare', 'ashare'],
        default='tushare',
        help="Data source to use (tushare or ashare). Default is tushare."
    )
    parser.add_argument(
        "--view",
        action='store_true',
        help="View latest data records for the specified stock code."
    )
    
    args = parser.parse_args()
    
    # Initialize the data fetcher
    fetcher = StockDataFetcher()
    
    if args.view:
        # View latest data records
        fetcher.view_latest_data(args.source, args.stock_code)
    else:
        # Fetch and store data based on the selected source
        fetcher.fetch_and_store_data(args.source, args.stock_code, args.days_back)

if __name__ == "__main__":
    # Ensure the database is initialized before doing anything else
    db_manager = DatabaseManager()
    main()