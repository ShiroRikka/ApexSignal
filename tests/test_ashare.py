from api.ashare_client import AshareClient
import pandas as pd

def main():
    # Initialize the Ashare client
    client = AshareClient()

    # Define the stock code for Ping An Bank (601818) in the format expected by Ashare
    stock_code = 'sh601818'  # Ashare uses 'sh' prefix for Shanghai stocks

    # Fetch recent daily data (e.g., last 10 trading days)
    print(f"Fetching recent daily data for {stock_code}...")
    daily_data = client.get_price(code=stock_code, frequency='1d', count=10)
    print(daily_data)
    print("\n---\n")

    # Fetch recent 1-hour data (e.g., last 10 hours)
    print(f"Fetching recent 1-hour data for {stock_code}...")
    hourly_data = client.get_price(code=stock_code, frequency='60m', count=10)
    print(hourly_data)
    print("\n---\n")

if __name__ == '__main__':
    main()