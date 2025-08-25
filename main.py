import time
import datetime
from database_manager import create_connection, create_tables, get_stock_data
from stock_data_processor import fetch_historical_daily_data, fetch_intraday_data, calculate_and_store_indicators_from_combined_data

def main():
    db_file = "stock_data.db"
    conn = create_connection(db_file)

    if conn:
        create_tables(conn)
        print(f"Database '{db_file}' and tables are ready.")

        # List of stock codes to monitor
        stock_codes = ['sh601818'] # Example: Ping An Bank (Shanghai stock)
        
        # --- Initialization Phase ---
        print("\n--- Initialization Phase: Fetching Historical Data ---")
        historical_data_map = {} # To store historical DataFrames for each stock
        for stock_code in stock_codes:
            # Fetch 59 days of historical data. This data is static for the day.
            # We assume get_stock_data can retrieve this, or we fetch it fresh.
            # For simplicity, we fetch it fresh every time the script starts.
            # A more advanced system would check if historical data is already up-to-date.
            historical_df = fetch_historical_daily_data(conn, stock_code, count=59)
            if not historical_df.empty:
                historical_data_map[stock_code] = historical_df
            else:
                print(f"Could not fetch historical data for {stock_code}. Skipping this stock.")
        
        if not historical_data_map:
            print("No historical data fetched for any stock. Exiting.")
            conn.close()
            return

        # --- Real-time Monitoring Phase ---
        print("\n--- Real-time Monitoring Phase ---")
        # Intraday frequency and polling interval
        intraday_frequency = '1m' # 1-minute data for real-time updates
        polling_interval = 60    # Poll every 60 seconds

        print(f"Starting real-time monitoring for {list(historical_data_map.keys())} every {polling_interval} seconds...")
        print(f"Using historical data (59 days) + latest intraday data ('{intraday_frequency}') for indicator calculation.")

        try:
            while True:
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"\n[{current_time}] Fetching intraday data and updating indicators...")
                
                for stock_code, historical_df in historical_data_map.items():
                    # Fetch the latest intraday data point
                    intraday_df = fetch_intraday_data(stock_code, frequency=intraday_frequency, count=1)
                    
                    # Calculate and store indicators based on combined data
                    # This function now handles the logic of combining and calculating
                    calculate_and_store_indicators_from_combined_data(conn, stock_code, historical_df, intraday_df)
                
                print(f"Waiting for {polling_interval} seconds...")
                time.sleep(polling_interval)

        except KeyboardInterrupt:
            print("\nStopping data collection.")
        finally:
            conn.close()
            print("Database connection closed.")
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()
