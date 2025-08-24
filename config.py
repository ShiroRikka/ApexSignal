"""Configuration module for the stock data collector."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('.env')

# Tushare API configuration
TUSHARE_TOKEN = os.environ.get('TUSHARE_TOKEN')
if not TUSHARE_TOKEN:
    raise ValueError("TUSHARE_TOKEN not found in environment variables. Please set it in the .env file.")

# Database configuration
DB_NAME = 'stock_data.db'

# Default stock code and date range for data fetching
DEFAULT_STOCK_CODE = '601818.SH'
DEFAULT_DAYS_BACK = 365