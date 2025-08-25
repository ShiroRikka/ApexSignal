"""Main entry point for the stock data collector application."""

import argparse
import os
import sqlite3
from data.data_fetcher import StockDataFetcher
from config import DEFAULT_STOCK_CODE, DEFAULT_DAYS_BACK
from database.db_manager import DatabaseManager

def main():
    """Main function to parse arguments and initiate data fetching."""
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
    
    # Fetch and store data based on the selected source
    if not args.view:
        if args.source == 'tushare':
            fetcher.fetch_and_store_data_tushare(args.stock_code, args.days_back)
        elif args.source == 'ashare':
            # For Ashare, we expect a simpler stock code format like '601818'
            stock_code = args.stock_code.split('.')[0]  # Extract '601818' from '601818.SH'
            fetcher.fetch_and_store_data_ashare(stock_code, args.days_back)
    else:
        # View latest data records
        db_manager = DatabaseManager()
        source = args.source
        # For viewing, we need to use the correct stock code format for each source
        stock_code = args.stock_code if source == 'tushare' else args.stock_code.split('.')[0]
        
        print(f"\n--- Latest Daily Price Data from {source} ---")
        daily_records = db_manager.get_latest_data('daily_price', source, stock_code, 5)
        if daily_records:
            for record in daily_records:
                print(record)
        else:
            print("No daily price data found for the specified stock code.")
            
        print(f"\n--- Latest Indicators Data from {source} ---")
        indicator_records = db_manager.get_latest_data('indicators', source, stock_code, 5)
        if indicator_records:
            for record in indicator_records:
                print(record)
        else:
            print("No indicators data found for the specified stock code.")

if __name__ == "__main__":
    # Ensure the database is initialized before doing anything else
    db_manager = DatabaseManager()
    main()