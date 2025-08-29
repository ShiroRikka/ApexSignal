# Stock Data Collector Project Context

## Project Overview

This project is a Python application designed to fetch, store, and analyze Chinese A-share stock market data. It primarily utilizes the **Ashare** library for real-time data retrieval and the **MyTT** library for technical analysis. The project also lists dependencies on other data sources like `tushare`, `akshare`, and `baostock` in its configuration files (`pyproject.toml`, `requirements.txt`), suggesting potential future expansion or alternative data sources.

Key features of the core `Ashare` component:
- **Simplified API**: Provides a single `get_price()` function to access various types of stock data (daily, weekly, monthly, minute-level).
- **Dual Data Sources**: Automatically switches between Sina Finance and Tencent Finance for data retrieval, providing fault tolerance.
- **Data Format**: Returns data in pandas DataFrame format, making it easy to work with for analysis.
- **Lightweight**: The core library is contained in a single file (`Ashare.py`), making it easy to integrate.

The `MyTT` component is a Python implementation of technical analysis indicators commonly found in trading platforms like TDX (Tongdaxin) and TongHuaShun, such as MA, BOLL, MACD, KDJ, etc.

## Getting Started / Running the Project

Based on the project files, there isn't a single, clearly defined main entry point or a standard set of run scripts defined in `pyproject.toml`. The project appears to be a collection of libraries and examples. To use it, you would typically run the example scripts or integrate the libraries into your own Python code.

1.  **Set up the environment**: Ensure Python 3.13+ is installed. Install dependencies using `uv` or `pip`.
    ```bash
    # Using uv (recommended if you have it)
    uv sync
    # Or, based on pyproject.toml
    pip install .
    ```
2.  **Run Examples**: You can execute the example scripts provided in the project root to see the libraries in action.
    ```bash
    # Navigate to the project root
    cd C:\Users\29857\Documents\Github\ApexSignal
    # Run get_stock_data.py to see basic data fetching and indicator calculation
    python get_stock_data.py
    ```
3.  **Use in your code**: Import the libraries (`from Ashare import *`, `from MyTT import *`) into your Python scripts and use the `get_price()` function and technical indicator functions as demonstrated in the demo files.

## Development Conventions & Practices

- **Dependencies**: Dependencies are managed using `pyproject.toml` and `requirements.txt`. `uv` is likely the preferred package manager.
- **Libraries**: The core functionality resides in `Ashare.py` and `MyTT.py`. These are standalone modules.
- **Examples**: Usage examples are provided in `get_stock_data.py`.
- **Data Handling**: The project heavily relies on `pandas` DataFrames for data manipulation and `numpy` for numerical computations within `MyTT`.
- **API Usage**: The `Ashare` library fetches data via HTTP requests to public financial APIs (Sina, Tencent).
