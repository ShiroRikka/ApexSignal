"""Utility functions for processing Ashare data."""

import pandas as pd


def process_ashare_data(df_daily, stock_code):
    """
    Process raw Ashare data to match the database schema.

    Args:
        df_daily (pandas.DataFrame): Raw data fetched from Ashare API.
        stock_code (str): The original stock code (e.g., '601818').

    Returns:
        pandas.DataFrame: Processed data.
    """
    if df_daily is None or df_daily.empty:
        return df_daily
        
    # Add ts_code column to match database schema
    df_daily['ts_code'] = stock_code  # Store original code without 'sh'/'sz' prefix
    
    # Add trade_date column from index
    df_daily['trade_date'] = df_daily.index.strftime('%Y%m%d')
    
    # Rename columns to match database schema
    df_daily.rename(columns={
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'volume': 'vol'
    }, inplace=True)
    
    # Add missing 'amount' column with default value 0.0
    df_daily['amount'] = 0.0
    
    # Reorder columns to match database schema
    expected_columns = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount']
    df_daily = df_daily[expected_columns]
    
    return df_daily