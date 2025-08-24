"""Test script for indicator calculation functionality."""

import pandas as pd
import numpy as np
from utils.indicator_calculator import IndicatorCalculator

def test_macd():
    """Test the MACD calculation functionality."""
    # Create sample data with clear price movements
    data = {
        'ts_code': ['000001.SZ'] * 15,
        'trade_date': [f'202301{i:02d}' for i in range(1, 16)],
        'open': [10.0, 10.2, 10.1, 10.3, 10.5, 10.4, 10.6, 10.8, 10.7, 10.9,
                 11.1, 11.0, 11.2, 11.4, 11.3],
        'high': [10.5, 10.6, 10.7, 10.8, 11.0, 10.9, 11.1, 11.2, 11.1, 11.3,
                 11.5, 11.4, 11.6, 11.8, 11.7],
        'low': [9.9, 10.0, 10.0, 10.1, 10.3, 10.2, 10.4, 10.6, 10.5, 10.7,
                10.9, 10.8, 11.0, 11.2, 11.1],
        'close': [10.2, 10.1, 10.3, 10.5, 10.4, 10.6, 10.8, 10.7, 10.9, 11.1,
                  11.0, 11.2, 11.4, 11.3, 11.5],
        'vol': [1000000] * 15,
        'amount': [10000000] * 15
    }
    
    df = pd.DataFrame(data)
    
    # Create indicator calculator
    calculator = IndicatorCalculator(df)
    
    # Calculate MACD
    result = calculator.calculate_macd()
    
    # Print MACD results
    print("MACD calculation results:")
    print(result[['trade_date', 'close', 'macd_dif', 'macd_dea', 'macd_bar']].to_string(index=False))

def test_kdj():
    """Test the KDJ calculation functionality."""
    # Create sample data with clear price movements
    data = {
        'ts_code': ['000001.SZ'] * 15,
        'trade_date': [f'202301{i:02d}' for i in range(1, 16)],
        'open': [10.0, 10.2, 10.1, 10.3, 10.5, 10.4, 10.6, 10.8, 10.7, 10.9,
                 11.1, 11.0, 11.2, 11.4, 11.3],
        'high': [10.5, 10.6, 10.7, 10.8, 11.0, 10.9, 11.1, 11.2, 11.1, 11.3,
                 11.5, 11.4, 11.6, 11.8, 11.7],
        'low': [9.9, 10.0, 10.0, 10.1, 10.3, 10.2, 10.4, 10.6, 10.5, 10.7,
                10.9, 10.8, 11.0, 11.2, 11.1],
        'close': [10.2, 10.1, 10.3, 10.5, 10.4, 10.6, 10.8, 10.7, 10.9, 11.1,
                  11.0, 11.2, 11.4, 11.3, 11.5],
        'vol': [1000000] * 15,
        'amount': [10000000] * 15
    }
    
    df = pd.DataFrame(data)
    
    # Create indicator calculator
    calculator = IndicatorCalculator(df)
    
    # Calculate KDJ
    result = calculator.calculate_kdj(period=9)
    
    # Print KDJ results
    print("\nKDJ calculation results:")
    print(result[['trade_date', 'close', 'kdj_k', 'kdj_d', 'kdj_j']].to_string(index=False))

def test_rsi():
    """Test the RSI calculation functionality."""
    # Create sample data with a clear upward trend followed by a downward trend
    data = {
        'ts_code': ['000001.SZ'] * 20,
        'trade_date': [f'202301{i:02d}' for i in range(1, 21)],
        'open': [10.0, 10.2, 10.1, 10.3, 10.5, 10.4, 10.6, 10.8, 10.7, 10.9,
                 11.1, 11.0, 11.2, 11.4, 11.3, 11.5, 11.7, 11.6, 11.8, 12.0],
        'high': [10.5, 10.6, 10.7, 10.8, 11.0, 10.9, 11.1, 11.2, 11.1, 11.3,
                 11.5, 11.4, 11.6, 11.8, 11.7, 11.9, 12.1, 12.0, 12.2, 12.4],
        'low': [9.9, 10.0, 10.0, 10.1, 10.3, 10.2, 10.4, 10.6, 10.5, 10.7,
                10.9, 10.8, 11.0, 11.2, 11.1, 11.3, 11.5, 11.4, 11.6, 11.8],
        'close': [10.2, 10.1, 10.3, 10.5, 10.4, 10.6, 10.8, 10.7, 10.9, 11.1,
                  11.0, 11.2, 11.4, 11.3, 11.5, 11.7, 11.6, 11.8, 12.0, 11.9],
        'vol': [1000000] * 20,
        'amount': [10000000] * 20
    }
    
    df = pd.DataFrame(data)
    
    # Create indicator calculator
    calculator = IndicatorCalculator(df)
    
    # Calculate RSI
    result = calculator.calculate_rsi(period=14)
    
    # Print RSI results
    print("\nRSI14 calculation results:")
    print(result[['trade_date', 'close', 'rsi']].to_string(index=False))

def test_all_indicators():
    """Test all indicator calculation functionality."""
    # Create sample data
    data = {
        'ts_code': ['000001.SZ'] * 20,
        'trade_date': [f'202301{i:02d}' for i in range(1, 21)],
        'open': [10.0, 10.2, 10.1, 10.3, 10.5, 10.4, 10.6, 10.8, 10.7, 10.9,
                 11.1, 11.0, 11.2, 11.4, 11.3, 11.5, 11.7, 11.6, 11.8, 12.0],
        'high': [10.5, 10.6, 10.7, 10.8, 11.0, 10.9, 11.1, 11.2, 11.1, 11.3,
                 11.5, 11.4, 11.6, 11.8, 11.7, 11.9, 12.1, 12.0, 12.2, 12.4],
        'low': [9.9, 10.0, 10.0, 10.1, 10.3, 10.2, 10.4, 10.6, 10.5, 10.7,
                10.9, 10.8, 11.0, 11.2, 11.1, 11.3, 11.5, 11.4, 11.6, 11.8],
        'close': [10.2, 10.1, 10.3, 10.5, 10.4, 10.6, 10.8, 10.7, 10.9, 11.1,
                  11.0, 11.2, 11.4, 11.3, 11.5, 11.7, 11.6, 11.8, 12.0, 11.9],
        'vol': [1000000] * 20,
        'amount': [10000000] * 20
    }
    
    df = pd.DataFrame(data)
    
    # Create indicator calculator
    calculator = IndicatorCalculator(df)
    
    # Calculate all indicators
    result = calculator.calculate_all_indicators()
    
    # Print results
    print("\nSample data with all calculated indicators:")
    print(result[['ts_code', 'trade_date', 'close', 'macd_dif', 'macd_dea', 'macd_bar', 'rsi', 'kdj_k', 'kdj_d', 'kdj_j']].to_string(index=False))

if __name__ == "__main__":
    test_macd()
    test_kdj()
    test_rsi()
    test_all_indicators()