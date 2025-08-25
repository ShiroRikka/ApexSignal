"""Utility functions for the stock data collector."""

import pandas as pd


def convert_tushare_to_ashare_code(code):
    """
    Convert Tushare stock code format to Ashare format.
    
    Args:
        code (str): Stock code in Tushare format (e.g., '000001.SZ' or '600000.SH').
        
    Returns:
        str: Stock code in Ashare format (e.g., 'sz000001' or 'sh600000').
    """
    if '.' in code:
        if code.endswith('.XSHG'):
            return 'sh' + code[:6]
        elif code.endswith('.XSHE'):
            return 'sz' + code[:6]
    return code