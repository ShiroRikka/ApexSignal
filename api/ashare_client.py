"""Ashare API client for fetching real-time stock data.
Based on the open-source project Ashare: https://github.com/mpquant/Ashare
"""

import json
import requests
import datetime
import pandas as pd

class AshareClient:
    """A wrapper class for the Ashare API to fetch real-time stock data."""

    def __init__(self):
        """Initialize the Ashare client."""
        print("--- Ashare API client initialized ---")

    def _get_price_day_tx(self, code, end_date='', count=10, frequency='1d'):
        """
        Get daily price data from Tencent interface.
        
        Args:
            code (str): Stock code.
            end_date (str): End date in 'YYYY-MM-DD' format.
            count (int): Number of data points.
            frequency (str): Data frequency.
            
        Returns:
            pandas.DataFrame: DataFrame with price data.
        """
        unit = 'week' if frequency in '1w' else 'month' if frequency in '1M' else 'day'
        # Determine day, week, or month line
        if end_date:
            end_date = end_date.strftime('%Y-%m-%d') if isinstance(end_date, datetime.date) else end_date.split(' ')[0]
        end_date = '' if end_date == datetime.datetime.now().strftime('%Y-%m-%d') else end_date  # If date is today, make it empty
        URL = f'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},{unit},,{end_date},{count},qfq'
        st = json.loads(requests.get(URL).content)
        ms = 'qfq' + unit
        stk = st['data'][code]
        buf = stk[ms] if ms in stk else stk[unit]  # Index returns day, not qfqday
        df = pd.DataFrame(buf, columns=['time', 'open', 'close', 'high', 'low', 'volume'], dtype='float')
        df.time = pd.to_datetime(df.time)
        df.set_index(['time'], inplace=True)
        df.index.name = ''  # Handle index
        return df

    def _get_price_min_tx(self, code, end_date=None, count=10, frequency='1d'):
        """
        Get minute price data from Tencent interface.
        
        Args:
            code (str): Stock code.
            end_date (str): End date in 'YYYY-MM-DD' format.
            count (int): Number of data points.
            frequency (str): Data frequency.
            
        Returns:
            pandas.DataFrame: DataFrame with price data.
        """
        ts = int(frequency[:-1]) if frequency[:-1].isdigit() else 1  # Parse K-line period
        if end_date:
            end_date = end_date.strftime('%Y-%m-%d') if isinstance(end_date, datetime.date) else end_date.split(' ')[0]
        URL = f'http://ifzq.gtimg.cn/appstock/app/kline/mkline?param={code},m{ts},,{count}'
        st = json.loads(requests.get(URL).content)
        buf = st['data'][code]['m' + str(ts)]
        df = pd.DataFrame(buf, columns=['time', 'open', 'close', 'high', 'low', 'volume', 'n1', 'n2'])
        df = df[['time', 'open', 'close', 'high', 'low', 'volume']]
        df[['open', 'close', 'high', 'low', 'volume']] = df[['open', 'close', 'high', 'low', 'volume']].astype('float')
        df.time = pd.to_datetime(df.time)
        df.set_index(['time'], inplace=True)
        df.index.name = ''  # Handle index
        df['close'][-1] = float(st['data'][code]['qt'][code][3])  # Latest fund data is 3 digits
        return df

    def _get_price_sina(self, code, end_date='', count=10, frequency='60m'):
        """
        Get price data from Sina interface for all periods.
        Minute lines: 5m, 15m, 30m, 60m
        Daily line: 1d=240m
        Weekly line: 1w=1200m
        Monthly line: 1M=7200m
        
        Args:
            code (str): Stock code.
            end_date (str): End date in 'YYYY-MM-DD' format.
            count (int): Number of data points.
            frequency (str): Data frequency.
            
        Returns:
            pandas.DataFrame: DataFrame with price data.
        """
        frequency = frequency.replace('1d', '240m').replace('1w', '1200m').replace('1M', '7200m')
        mcount = count
        ts = int(frequency[:-1]) if frequency[:-1].isdigit() else 1  # Parse K-line period
        if (end_date != '') & (frequency in ['240m', '1200m', '7200m']):
            end_date = pd.to_datetime(end_date) if not isinstance(end_date, datetime.date) else end_date  # Convert to datetime
            unit = 4 if frequency == '1200m' else 29 if frequency == '7200m' else 1  # 4, 29 - a few more data points don't affect speed
            count = count + (datetime.datetime.now() - end_date).days // unit  # How many natural days from end date to today (definitely > trading days)
            # print(code,end_date,count)
        URL = f'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={code}&scale={ts}&ma=5&datalen={count}'
        dstr = json.loads(requests.get(URL).content)
        # df=pd.DataFrame(dstr,columns=['day','open','high','low','close','volume'],dtype='float')
        df = pd.DataFrame(dstr, columns=['day', 'open', 'high', 'low', 'close', 'volume'])
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)  # Convert data types
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        df.day = pd.to_datetime(df.day)
        df.set_index(['day'], inplace=True)
        df.index.name = ''  # Handle index
        if (end_date != '') & (frequency in ['240m', '1200m', '7200m']):
            return df[df.index <= end_date][-mcount:]  # Return daily line with end date first
        return df

    def get_price(self, code, frequency='1d', count=10, end_date=''):
        """
        Fetch stock price data for a given stock code and parameters.

        Args:
            code (str): The stock code (e.g., 'sh000001' or '000001.XSHG').
            frequency (str): Data frequency ('1d', '1w', '1M', '1m', '5m', '15m', '30m', '60m'). Default is '1d'.
            count (int): Number of data points to fetch. Default is 10.
            end_date (str): End date for historical data in 'YYYY-MM-DD' format. Default is empty (today).

        Returns:
            pandas.DataFrame: A DataFrame containing the price data.
        """
        # Compatible processing of security code encoding
        xcode = code.replace('.XSHG', '').replace('.XSHE', '')
        xcode = 'sh' + xcode if ('XSHG' in code) else 'sz' + xcode if ('XSHE' in code) else code

        if frequency in ['1d', '1w', '1M']:  # 1d daily, 1w weekly, 1M monthly
            try:
                return self._get_price_sina(xcode, end_date=end_date, count=count, frequency=frequency)  # Primary
            except requests.RequestException:
                return self._get_price_day_tx(xcode, end_date=end_date, count=count,
                                              frequency=frequency)  # Backup

        if frequency in ['1m', '5m', '15m', '30m', '60m']:  # Minute lines, 1m only has Tencent interface, 5m 5 minutes, 60m 60 minutes
            if frequency in '1m':
                return self._get_price_min_tx(xcode, end_date=end_date, count=count, frequency=frequency)
            try:
                return self._get_price_sina(xcode, end_date=end_date, count=count, frequency=frequency)  # Primary
            except requests.RequestException:
                return self._get_price_min_tx(xcode, end_date=end_date, count=count, frequency=frequency)  # Backup

        print(f"Unsupported frequency: {frequency}.")
        return pd.DataFrame()  # Return empty DataFrame for unsupported frequencies