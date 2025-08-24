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
        Calculate RSI indicator using Wilder's Smoothing Method.

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
        
        # Calculate initial average gain and loss using simple moving average
        avg_gain = gain.rolling(window=period, min_periods=period).mean()
        avg_loss = loss.rolling(window=period, min_periods=period).mean()
        
        # Apply Wilder's smoothing method for subsequent values
        for i in range(period, len(self.data)):
            avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period - 1) + gain.iloc[i]) / period
            avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period - 1) + loss.iloc[i]) / period
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Add to data
        self.data['rsi'] = rsi
        
        return self.data
    
    def calculate_kdj(self, period=9):
        """
        Calculate KDJ indicator using standard weighted moving average method.

        Args:
            period (int): Period for calculating highest high and lowest low. Default is 9.

        Returns:
            pd.DataFrame: DataFrame with added KDJ columns.
        """
        # Calculate highest high and lowest low over the period
        low_min = self.data['low'].rolling(window=period, min_periods=period).min()
        high_max = self.data['high'].rolling(window=period, min_periods=period).max()
        
        # Calculate RSV (Raw Stochastic Value)
        rsv = 100 * (self.data['close'] - low_min) / (high_max - low_min)
        
        # Initialize K and D arrays
        k = np.zeros(len(self.data))
        d = np.zeros(len(self.data))
        
        # Set initial values for K and D
        # Find the first valid RSV value
        first_valid_index = rsv.first_valid_index()
        if first_valid_index is not None:
            # Set initial K and D values to 50
            k[first_valid_index] = 50
            d[first_valid_index] = 50
            
            # Calculate K and D using weighted moving average
            for i in range(first_valid_index + 1, len(self.data)):
                k[i] = (2/3) * k[i-1] + (1/3) * rsv.iloc[i]
                d[i] = (2/3) * d[i-1] + (1/3) * k[i]
        else:
            # If no valid RSV values, set all K and D values to NaN
            k[:] = np.nan
            d[:] = np.nan
        
        # Calculate J value
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