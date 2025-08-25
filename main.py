import time
import datetime
from database_manager import create_connection, create_tables
from stock_data_processor import fetch_and_store_stock_data, calculate_and_store_indicators

def main():
    db_file = "stock_data.db"
    conn = create_connection(db_file)

    if conn:
        create_tables(conn)
        print(f"Database '{db_file}' and tables are ready.")

        # List of stock codes to monitor (example: Ping An Bank, Kweichow Moutai)
        # Note: Ashare uses 'sh' or 'sz' prefix for some functions, and '.XSHG' or '.XSHE' suffix for others.
        # The get_price function in Ashare.py handles this conversion internally.
        stock_codes = ['601818.SH'] # Example: Ping An Bank, Kweichow Moutai, China Merchants Bank
        
        # Fetch frequency and count
        frequency = '1m' # 1-minute data
        count = 60       # Fetch last 60 minutes of data
        
        # Polling interval in seconds (e.g., 60 seconds for 1-minute data)
        polling_interval = 60

        print(f"Starting real-time data collection for {stock_codes} every {polling_interval} seconds...")

        try:
            while True:
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"\n[{current_time}] Fetching and processing data...")
                
                for stock_code in stock_codes:
                    # Fetch and store stock data
                    stock_df = fetch_and_store_stock_data(conn, stock_code, frequency, count)
                    
                    # Calculate and store indicators if data was fetched
                    if not stock_df.empty:
                        calculate_and_store_indicators(conn, stock_code, stock_df)
                
                print(f"Waiting for {polling_interval} seconds...")
                time.sleep(polling_interval)

        except KeyboardInterrupt:
            print("Stopping data collection.")
        finally:
            conn.close()
            print("Database connection closed.")
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()
