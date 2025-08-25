"""Test script to verify the modifications to the stock data collector."""

import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.code_converter import convert_tushare_to_ashare_code
from data.data_fetcher import StockDataFetcher


def test_code_converter():
    """Test the code converter function."""
    print("Testing code converter...")
    
    # Test cases
    test_cases = [
        ('000001.SZ', 'sz000001'),
        ('600000.SH', 'sh600000'),
        ('000001.XSHE', 'sz000001'),
        ('600000.XSHG', 'sh600000'),
        ('601818', 'sh601818'),
        ('000001', 'sz000001'),
        ('sh601818', 'sh601818'),
        ('sz000001', 'sz000001')
    ]
    
    for input_code, expected_output in test_cases:
        result = convert_tushare_to_ashare_code(input_code)
        if result == expected_output:
            print(f"  PASS: {input_code} -> {result}")
        else:
            print(f"  FAIL: {input_code} -> {result} (expected {expected_output})")


def test_data_fetcher():
    """Test the data fetcher classes."""
    print("\nTesting data fetcher...")
    
    # Create a StockDataFetcher instance
    fetcher = StockDataFetcher()
    
    # Check if the fetcher has the required attributes
    if hasattr(fetcher, 'tushare_fetcher') and hasattr(fetcher, 'ashare_fetcher'):
        print("  PASS: StockDataFetcher has tushare_fetcher and ashare_fetcher attributes")
    else:
        print("  FAIL: StockDataFetcher missing required attributes")
        
    # Check if the sub-fetchers have the required attributes
    if hasattr(fetcher.tushare_fetcher, 'client') and hasattr(fetcher.tushare_fetcher, 'db_manager'):
        print("  PASS: TushareDataFetcher has client and db_manager attributes")
    else:
        print("  FAIL: TushareDataFetcher missing required attributes")
        
    if hasattr(fetcher.ashare_fetcher, 'client') and hasattr(fetcher.ashare_fetcher, 'db_manager'):
        print("  PASS: AshareDataFetcher has client and db_manager attributes")
    else:
        print("  FAIL: AshareDataFetcher missing required attributes")


if __name__ == "__main__":
    test_code_converter()
    test_data_fetcher()
    print("\nAll tests completed.")