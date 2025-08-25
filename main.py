"""Main entry point for the stock data collector application."""

import argparse
from data.data_fetcher import StockDataFetcher
from data.ashare_data_fetcher import AshareDataFetcher
from utils.code_converter import convert_tushare_to_ashare_code
from config import DEFAULT_STOCK_CODE, DEFAULT_DAYS_BACK

def main():
    """Main function to parse arguments and initiate data fetching."""
    parser = argparse.ArgumentParser(description="Fetch and store Chinese A-share stock data.")
    parser.add_argument(
        "--stock_code",
        type=str,
        default=DEFAULT_STOCK_CODE,
        help=f"Stock code to fetch data for (e.g., 601818.SH). Default is {DEFAULT_STOCK_CODE}."
    )
    parser.add_argument(
        "--days_back",
        type=int,
        default=DEFAULT_DAYS_BACK,
        help=f"Number of days back to fetch data from today. Default is {DEFAULT_DAYS_BACK}."
    )
    parser.add_argument(
        "--api",
        type=str,
        choices=['tushare', 'ashare'],
        default='tushare',
        help="API to use for fetching data. Default is 'tushare'."
    )

    args = parser.parse_args()

    print("--- Starting Stock Data Collector ---")
    
    if args.api == 'tushare':
        fetcher = StockDataFetcher()
    else:
        fetcher = AshareDataFetcher()
        
    fetcher.fetch_and_store_data(stock_code=args.stock_code, days_back=args.days_back)
    print("--- Stock Data Collector finished ---")

if __name__ == "__main__":
    main()