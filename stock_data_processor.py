import pandas as pd
import datetime
import time
from Ashare.Ashare import get_price
from MyTT.MyTT import * # Import all technical indicators
from database_manager import create_connection, create_tables, insert_stock_data, insert_indicator_data, get_stock_data

def fetch_historical_daily_data(conn, stock_code, count=250):
    """ Fetches historical daily data and stores it in the database. """
    print(f"Fetching {count} days of historical daily data for {stock_code}...")
    try:
        df = get_price(code=stock_code, frequency='1d', count=count)
        if df is None:
            print(f"Failed to fetch historical data for {stock_code}. API returned None.")
            return pd.DataFrame()
        if not df.empty:
            # Before inserting, delete old historical data for this stock to avoid duplicates
            # This requires a new function in database_manager.py
            # For now, we'll just insert and handle potential duplicates if they arise
            # or assume the main loop handles this by fetching a fixed count.
            # A more robust solution would be to clear and repopulate historical data daily.
            insert_stock_data(conn, stock_code, df)
            print(f"Successfully fetched and stored {len(df)} historical records for {stock_code}.")
            return df
        else:
            print(f"No historical data fetched for {stock_code}.")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching historical data for {stock_code}: {e}")
        return pd.DataFrame()

def fetch_intraday_data(stock_code, frequency='1m', count=1):
    """ Fetches real-time intraday data. Does not store by itself. """
    print(f"Fetching latest {count} {frequency} intraday data for {stock_code}...")
    try:
        df = get_price(code=stock_code, frequency=frequency, count=count)
        if df is None:
            print(f"Failed to fetch intraday data for {stock_code}. API returned None.")
            return pd.DataFrame()
        return df
    except Exception as e:
        print(f"Error fetching intraday data for {stock_code}: {e}")
        return pd.DataFrame()

def calculate_and_store_indicators_from_combined_data(conn, stock_code, historical_df, intraday_df):
    """ Combines historical and intraday data, calculates indicators, and stores them. """
    if historical_df.empty:
        print(f"No historical data to combine for {stock_code}.")
        return

    # Combine historical data with the latest intraday data point
    # We only need the latest row from intraday data for indicator calculation
    if intraday_df.empty:
        print(f"No intraday data to combine for {stock_code}. Using only historical data.")
        combined_df = historical_df
    else:
        # Ensure no duplicate timestamps, e.g., if intraday_df's last timestamp is already in historical_df
        # This is a simple append; more sophisticated merging might be needed depending on data structure
        latest_intraday_row = intraday_df.tail(1)
        # A simple check to avoid duplicating the last historical day if intraday is for the same day
        # This assumes historical_df.index is date-only and intraday_df.index is datetime
        # A more robust check would compare dates.
        if not historical_df.empty and latest_intraday_row.index[0].date() == historical_df.index[-1].date():
             # If the intraday data is for the same day as the last historical day,
             # we might want to replace it or handle it differently.
             # For simplicity, we'll just append, which might lead to a duplicate day's data
             # if not handled by the database or indicator logic.
             # A better approach: historical_df should be up to yesterday, intraday_df is today.
             pass # For now, just append

        combined_df = pd.concat([historical_df, latest_intraday_row])
    
    # Recalculate indicators on the full combined dataset
    print(f"Calculating indicators for {stock_code} based on combined data...")
    C = combined_df['close'].values
    H = combined_df['high'].values
    L = combined_df['low'].values
    # O and V are not used by current indicators but good to have for consistency
    # O = combined_df['open'].values
    # V = combined_df['volume'].values

    DIF, DEA, MACD_val = MACD(C)
    RSI_val = RSI(C, N=14)
    K, D, J = KDJ(C, H, L)

    # We are only interested in the indicator values for the latest timestamp (from intraday data)
    latest_timestamp = combined_df.index[-1]
    indicators_dict = {}

    if not pd.isna(DIF[-1]): indicators_dict['MACD_DIF'] = DIF[-1]
    if not pd.isna(DEA[-1]): indicators_dict['MACD_DEA'] = DEA[-1]
    if not pd.isna(MACD_val[-1]): indicators_dict['MACD'] = MACD_val[-1]
    if not pd.isna(RSI_val[-1]): indicators_dict['RSI'] = RSI_val[-1]
    if not pd.isna(K[-1]): indicators_dict['KDJ_K'] = K[-1]
    if not pd.isna(D[-1]): indicators_dict['KDJ_D'] = D[-1]
    if not pd.isna(J[-1]): indicators_dict['KDJ_J'] = J[-1]
    
    if indicators_dict:
        # This function should ideally update/replace the latest indicator for the timestamp
        # For now, it just inserts, which might lead to multiple entries for the same minute if not handled by DB schema
        insert_indicator_data(conn, stock_code, latest_timestamp, indicators_dict)
        print(f"Successfully calculated and stored latest indicators for {stock_code} at {latest_timestamp}.")
    else:
        print(f"No valid indicators calculated for {stock_code} at {latest_timestamp}.")

# The old fetch_and_store_stock_data is now split and its logic is in main.py
# We can keep it for standalone testing or remove it.
# For now, let's comment out its usage in the __main__ block.

def calculate_and_store_indicators(conn, stock_code, df):
    """ Calculates technical indicators using MyTT and stores them in the database. """
    if df.empty:
        print(f"No stock data to calculate indicators for {stock_code}.")
        return

    print(f"Calculating indicators for {stock_code}...")
    # Ensure the DataFrame has the required columns for MyTT
    C = df['close'].values
    O = df['open'].values
    H = df['high'].values
    L = df['low'].values
    V = df['volume'].values

    # Calculate all indicators
    DIF, DEA, MACD_val = MACD(C)
    RSI_val = RSI(C, N=14)
    K, D, J = KDJ(C, H, L)

    # Store all indicators for each timestamp
    for i in range(len(df)):
        timestamp = df.index[i]
        indicators_dict = {}
        
        # Add MACD indicators
        if not pd.isna(DIF[i]):
            indicators_dict['MACD_DIF'] = DIF[i]
        if not pd.isna(DEA[i]):
            indicators_dict['MACD_DEA'] = DEA[i]
        if not pd.isna(MACD_val[i]):
            indicators_dict['MACD'] = MACD_val[i]
        
        # Add RSI indicator
        if not pd.isna(RSI_val[i]):
            indicators_dict['RSI'] = RSI_val[i]
        
        # Add KDJ indicators
        if not pd.isna(K[i]):
            indicators_dict['KDJ_K'] = K[i]
        if not pd.isna(D[i]):
            indicators_dict['KDJ_D'] = D[i]
        if not pd.isna(J[i]):
            indicators_dict['KDJ_J'] = J[i]
        
        # Insert all indicators for this timestamp
        if indicators_dict:
            insert_indicator_data(conn, stock_code, timestamp, indicators_dict)

    print(f"Successfully calculated and stored indicators for {stock_code}.")

if __name__ == '__main__':
    db_file = "test_stock_data.db"
    conn = create_connection(db_file)
    if conn:
        create_tables(conn)
        
        # Example usage with a real stock code (e.g., Ping An Bank)
        stock_code = 'sh601818' # Replace with a valid stock code
        
        # Fetch and store historical data (e.g., 1 year / 250 trading days)
        historical_df = fetch_historical_daily_data(conn, stock_code, count=250)
        
        # Simulate fetching intraday data
        intraday_df = fetch_intraday_data(stock_code, frequency='1m', count=1)

        # Calculate and store indicators based on combined data
        if not historical_df.empty:
            calculate_and_store_indicators_from_combined_data(conn, stock_code, historical_df, intraday_df)

        conn.close()
    else:
        print("Error! Cannot create the database connection.")
