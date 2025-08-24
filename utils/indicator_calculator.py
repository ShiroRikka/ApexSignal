"""Module for calculating technical indicators like MACD, KDJ, RSI, etc."""

import pandas as pd
import numpy as np


class IndicatorCalculator:
    """A class to calculate various technical indicators."""

    def __init__(self, data: pd.DataFrame):
        """
        Initialize with stock price data.

        Args:
            data (pd.DataFrame): DataFrame containing stock price data with columns:
                                'ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount'
        """
        # Ensure data is sorted by trade_date in ascending order
        self.data = data.sort_values(by='trade_date', ascending=True).reset_index(drop=True)
        
    def calculate_macd(self, fast_period=12, slow_period=26, signal_period=9):
        """
        Calculate MACD indicator.

        Args:
            fast_period (int): Fast EMA period. Default is 12.
            slow_period (int): Slow EMA period. Default is 26.
            signal_period (int): Signal line EMA period. Default is 9.

        Returns:
            pd.DataFrame: DataFrame with added MACD columns.
        """
        # Calculate EMAs
        ema_fast = self.data['close'].ewm(span=fast_period, adjust=False).mean()
        ema_slow = self.data['close'].ewm(span=slow_period, adjust=False).mean()
        
        # Calculate MACD line
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        
        # Calculate MACD histogram
        macd_histogram = macd_line - signal_line
        
        # Add to data
        self.data['macd_line'] = macd_line
        self.data['signal_line'] = signal_line
        self.data['macd_histogram'] = macd_histogram
        
        return self.data
    
    def calculate_rsi(self, period=14):
        """
        Calculate RSI indicator.

        Args:
            period (int): RSI calculation period. Default is 14.

        Returns:
            pd.DataFrame: DataFrame with added RSI column.
        """
        # Calculate price changes
        delta = self.data['close'].diff()
        
        # Calculate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate average gains and losses
        avg_gain = gain.rolling(window=period, min_periods=1).mean()
        avg_loss = loss.rolling(window=period, min_periods=1).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Add to data
        self.data['rsi'] = rsi
        
        return self.data
    
    def calculate_kdj(self, period=9, k_period=3, d_period=3):
        """
        Calculate KDJ indicator.

        Args:
            period (int): Period for calculating highest high and lowest low. Default is 9.
            k_period (int): Smoothing period for %K. Default is 3.
            d_period (int): Smoothing period for %D. Default is 3.

        Returns:
            pd.DataFrame: DataFrame with added KDJ columns.
        """
        # Calculate highest high and lowest low over the period
        low_min = self.data['low'].rolling(window=period, min_periods=1).min()
        high_max = self.data['high'].rolling(window=period, min_periods=1).max()
        
        # Calculate %K
        stoch_k = 100 * (self.data['close'] - low_min) / (high_max - low_min)
        
        # Calculate %K smoothing
        k = stoch_k.rolling(window=k_period, min_periods=1).mean()
        
        # Calculate %D
        d = k.rolling(window=d_period, min_periods=1).mean()
        
        # Calculate %J
        j = 3 * k - 2 * d
        
        # Add to data
        self.data['kdj_k'] = k
        self.data['kdj_d'] = d
        self.data['kdj_j'] = j
        
        return self.data
    
    def calculate_all_indicators(self):
        """
        Calculate all supported indicators.

        Returns:
            pd.DataFrame: DataFrame with all calculated indicators.
        """
        self.calculate_macd()
        self.calculate_rsi()
        self.calculate_kdj()
        return self.data