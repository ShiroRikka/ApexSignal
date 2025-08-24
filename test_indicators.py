"""Test script for indicator calculation functionality."""

import pandas as pd
from utils.indicator_calculator import IndicatorCalculator

def test_indicators():
    """Test the indicator calculation functionality."""
    # Create sample data
    data = {
        'ts_code': ['000001.SZ'] * 10,
        'trade_date': ['20230101', '20230102', '20230103', '20230104', '20230105',
                      '20230106', '20230107', '20230108', '20230109', '20230110'],
        'open': [10.0, 10.2, 10.1, 10.3, 10.5, 10.4, 10.6, 10.8, 10.7, 10.9],
        'high': [10.5, 10.6, 10.7, 10.8, 11.0, 10.9, 11.1, 11.2, 11.1, 11.3],
        'low': [9.9, 10.0, 10.0, 10.1, 10.3, 10.2, 10.4, 10.6, 10.5, 10.7],
        'close': [10.2, 10.1, 10.3, 10.5, 10.4, 10.6, 10.8, 10.7, 10.9, 11.1],
        'vol': [1000000] * 10,
        'amount': [10000000] * 10
    }
    
    df = pd.DataFrame(data)
    
    # Create indicator calculator
    calculator = IndicatorCalculator(df)
    
    # Calculate all indicators
    result = calculator.calculate_all_indicators()
    
    # Print results
    print("Sample data with calculated indicators:")
    print(result[['ts_code', 'trade_date', 'close', 'macd_line', 'signal_line', 'macd_histogram', 'rsi', 'kdj_k', 'kdj_d', 'kdj_j']].to_string(index=False))

if __name__ == "__main__":
    test_indicators()