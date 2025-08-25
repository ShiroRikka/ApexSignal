# Stock Data Collector - Project Context

## Project Overview

This is a Python application designed to fetch, store, and potentially analyze Chinese A-share stock market data. It uses the Tushare `pro_bar` API interface to retrieve historical stock price information with forward-adjusted prices for accurate technical analysis, and stores this data in a local SQLite database. The application calculates technical indicators such as MACD, RSI14, and KDJ. It also supports fetching data from Ashare API as an alternative source.

### Core Technologies

*   **Language:** Python (>= 3.13)
*   **APIs:** Tushare Pro API (`pro_bar` interface) for stock data, Ashare API (based on [mpquant/Ashare](https://github.com/mpquant/Ashare))
*   **Data Processing:** `pandas`, `numpy`
*   **Database:** SQLite (`stock_data.db`)
*   **Dependencies:** Managed via `requirements.txt` or `pyproject.toml` (using `pandas-stubs`, `python-dotenv`, `requests`, `tushare`, `numpy`).

### Architecture

The project is structured into several modules:

1.  **`main.py`**: The main entry point. It parses command-line arguments (stock code, date range, data source) and initiates the data fetching process.
2.  **`config.py`**: Loads environment variables (like the Tushare API token) and defines default settings (database name, default stock code, default date range).
3.  **`api/`**: Contains API client implementations.
    *   `tushare_client.py`: Contains the `TushareClient` class, which wraps the Tushare Pro API calls using the `pro_bar` interface for fetching daily stock price data with forward adjustment.
    *   `ashare_client.py`: Contains the `AshareClient` class, which wraps the Ashare API calls for fetching daily stock price data.
4.  **`data/`**: Contains data processing modules.
    *   `data_fetcher.py`: Contains the `StockDataFetcher` class. This class orchestrates the workflow: it uses `TushareDataFetcher` or `AshareDataFetcher` to get data, checks the database for existing data using `DatabaseManager`, calculates technical indicators using `IndicatorCalculator`, and then saves both the raw data and indicators if needed.
    *   `tushare_data_fetcher.py`: Contains the `TushareDataFetcher` class, which handles data fetching and storing for Tushare API.
    *   `ashare_data_fetcher.py`: Contains the `AshareDataFetcher` class, which handles data fetching and storing for Ashare API.
5.  **`database/`**: Contains the database management module.
    *   `db_manager.py`: Contains the `DatabaseManager` class. It handles all interactions with the SQLite database, including initializing tables (`daily_price_tushare`, `daily_price_ashare`, `indicators_tushare`, `indicators_ashare`) and saving/fetching data. It maintains separate tables for data from different sources.
6.  **`utils/`**: Contains utility functions.
    *   `indicator_calculator.py`: Contains the `IndicatorCalculator` class, which calculates technical indicators (MACD, RSI14, KDJ) based on stock price data.
    *   `code_converter.py`: Contains utilities for converting stock code formats between Tushare and Ashare.
7.  **`scheduler/`**: An empty directory, likely intended for future scheduled task implementations (e.g., using `cron` or `APScheduler`).
8.  **`.env`**: A file (created by the user from `.env.example`) to store sensitive information like the Tushare API token.

## Building and Running

1.  **Setup:**
    *   Ensure Python 3.13+ is installed.
    *   Install dependencies: `pip install -r requirements.txt` (or `uv pip install -r requirements.txt`).
    *   Copy `.env.example` to `.env` and update `TUSHARE_TOKEN` with your actual Tushare API token.
2.  **Running:**
    *   Execute the main script: `python main.py`.
    *   **Optional Arguments:**
        *   `--stock_code <CODE>`: Specify the stock code (e.g., `000001.SZ`). Defaults to `601818.SH`.
        *   `--days_back <NUMBER>`: Specify the number of days back to fetch data. Defaults to `365`.
        *   `--source <tushare|ashare>`: Specify the data source to use. Defaults to `tushare`.
        *   `--view`: View the latest data records for the specified stock code.
3.  **Database:** The application automatically creates a SQLite database file named `stock_data.db` in the project root if it doesn't exist. It will create separate tables for daily prices and indicators for each data source (e.g., `daily_price_tushare`, `indicators_ashare`).

## Development Conventions

*   **Configuration:** Sensitive settings like API tokens are managed via environment variables loaded using `python-dotenv`. The `.env` file is not committed to version control (as per `.gitignore`).
*   **Dependencies:** Dependencies are listed in `requirements.txt` and defined in `pyproject.toml`.
*   **Module Structure:** Code is organized into modules (`api`, `data`, `database`, `utils`) to separate concerns.
*   **Error Handling:** Basic error handling is implemented in API calls and database operations, printing error messages to the console.
*   **Extensibility:** The indicator calculation module is designed to be easily extensible for adding more technical indicators in the future. The data fetching architecture also supports adding new data sources.