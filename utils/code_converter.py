"""Utility functions for the stock data collector."""


def convert_tushare_to_ashare_code(code):
    """
    Convert Tushare stock code format to Ashare format.
    
    Args:
        code (str): Stock code in Tushare format (e.g., '000001.SZ', '600000.SH', or '601818').
        
    Returns:
        str: Stock code in Ashare format (e.g., 'sz000001' or 'sh600000').
    """
    # Handle Tushare format with exchange suffix
    if code.endswith('.XSHG'):
        return 'sh' + code[:6]
    elif code.endswith('.XSHE'):
        return 'sz' + code[:6]
    elif code.endswith('.SH'):
        return 'sh' + code[:6]
    elif code.endswith('.SZ'):
        return 'sz' + code[:6]
    # Handle plain code (assuming SH for 6xxxxx, SZ for others)
    elif len(code) == 6 and code.isdigit():
        if code.startswith('6'):
            return 'sh' + code
        else:
            return 'sz' + code
    # If code is already in Ashare format, return as is
    elif code.startswith('sh') or code.startswith('sz'):
        return code
    # Default case - return the code as is
    else:
        return code