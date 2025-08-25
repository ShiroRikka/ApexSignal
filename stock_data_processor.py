import pandas as pd
import datetime
import time
from Ashare.Ashare import get_price
from MyTT.MyTT import * # Import all technical indicators
from database_manager import create_connection, create_tables, insert_stock_data, insert_indicator_data, get_stock_data

def fetch_and_store_stock_data(conn, stock_code, frequency='daily', count=60):
    """ Fetches daily stock data using Ashare and stores it in the database. """
    print(f"Fetching {count} {frequency} data for {stock_code}...")
    try:
        # Ashare's get_price function returns a DataFrame
        df = get_price(code=stock_code, frequency=frequency, count=count)
        if not df.empty:
            insert_stock_data(conn, stock_code, df)
            print(f"Successfully fetched and stored {len(df)} records for {stock_code}.")
            return df
        else:
            print(f"No data fetched for {stock_code}.")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching data for {stock_code}: {e}")
        return pd.DataFrame()

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
        stock_code = '601818' # Replace with a valid stock code
        
        # Fetch and store data
        stock_df = fetch_and_store_stock_data(conn, stock_code, frequency='daily', count=60) # Fetch 60 days of data
        
        # Calculate and store indicators
        if not stock_df.empty:
            calculate_and_store_indicators(conn, stock_code, stock_df)

        conn.close()
    else:
        print("Error! Cannot create the database connection.")
