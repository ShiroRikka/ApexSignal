# Stock Data Collector - Project Context

## Project Overview

This is a Python application designed to fetch, store, and potentially analyze Chinese A-share stock market data. It supports data retrieval from two sources:
1.  The Tushare `pro_bar` API interface for historical stock price data with forward-adjusted prices.
2.  The Ashare API (based on `mpquant/Ashare`) for real-time and historical stock price data.

It stores the fetched data in a local SQLite database and calculates technical indicators such as MACD, RSI14, and KDJ.

### Core Technologies

*   **Language:** Python (>= 3.13)
*   **APIs:**
    *   Tushare Pro API (`pro_bar` interface) for stock data.
    *   Ashare API (custom implementation based on `mpquant/Ashare`) for stock data.
*   **Data Processing:** `pandas`, `numpy`
*   **Database:** SQLite (`stock_data.db`)
*   **Dependencies:** Managed via `requirements.txt` or `pyproject.toml` (using `pandas-stubs`, `python-dotenv`, `requests`, `tushare`, `numpy`).

### Architecture

The project is structured into several modules:

1.  **`main.py`**: The main entry point. It parses command-line arguments (stock code, date range, data source) and initiates the data fetching process. It also supports viewing the latest stored data.
2.  **`config.py`**: Loads environment variables (like the Tushare API token) and defines default settings (database name, default stock code, default date range).
3.  **`api/tushare_client.py`**: Contains the `TushareClient` class, which wraps the Tushare Pro API calls using the `pro_bar` interface for fetching daily stock price data with forward adjustment.
4.  **`api/ashare_client.py`**: Contains the `AshareClient` class, which fetches stock data from the Ashare API.
5.  **`data/data_fetcher.py`**: Contains the `StockDataFetcher` class. This class orchestrates the workflow, delegating to specific fetcher classes (`TushareDataFetcher`, `AshareDataFetcher`) based on the source. These fetchers use their respective clients to get data, check the database for existing data using `DatabaseManager`, calculate technical indicators using `IndicatorCalculator`, and then save both the raw data and indicators if needed.
6.  **`database/db_manager.py`**: Contains the `DatabaseManager` class. It handles all interactions with the SQLite database, including initializing tables (`daily_price_tushare`, `daily_price_ashare`, `indicators_tushare`, `indicators_ashare`) and saving/fetching data. It maintains separate tables for data from different sources.
7.  **`utils/indicator_calculator.py`**: Contains the `IndicatorCalculator` class, which calculates technical indicators (MACD, RSI14, KDJ) based on stock price data.
8.  **`scheduler/`**: An empty directory, likely intended for future scheduled task implementations (e.g., using `cron` or `APScheduler`).
9.  **`utils/`**: Contains utility functions, including the technical indicator calculator.
10. **`.env`**: A file (created by the user from `.env.example`) to store sensitive information like the Tushare API token.

## Building and Running

1.  **Setup:**
    *   Ensure Python 3.13+ is installed.
    *   Install dependencies: `pip install -r requirements.txt` (or `uv pip install -r requirements.txt`).
    *   Copy `.env.example` to `.env` and update `TUSHARE_TOKEN` with your actual Tushare API token.
2.  **Running:**
    *   Execute the main script: `python main.py`.
    *   **Optional Arguments:**
        *   `--stock_code <CODE>`: Specify the stock code (e.g., `000001.SZ` for Tushare, `601818` for Ashare). Defaults to `601818.SH`.
        *   `--days_back <NUMBER>`: Specify the number of days back to fetch data. Defaults to `365`.
        *   `--source <tushare|ashare>`: Specify the data source. Defaults to `tushare`.
        *   `--view`: View the latest 5 records of daily price and indicator data for the specified stock code and source.
3.  **Database:** The application automatically creates a SQLite database file named `stock_data.db` in the project root if it doesn't exist. It will create separate tables for daily prices and indicators for each data source (e.g., `daily_price_tushare`, `indicators_ashare`).

## Development Conventions

*   **Configuration:** Sensitive settings like API tokens are managed via environment variables loaded using `python-dotenv`. The `.env` file is not committed to version control (as per `.gitignore`).
*   **Dependencies:** Dependencies are listed in `requirements.txt` and defined in `pyproject.toml`.
*   **Module Structure:** Code is organized into modules (`api`, `data`, `database`, `utils`) to separate concerns. Fetching logic is separated by data source.
*   **Database:** The database uses separate tables for data from different sources to avoid conflicts and ensure data integrity.
*   **Error Handling:** Basic error handling is implemented in API calls and database operations, printing error messages to the console.
*   **Extensibility:** The indicator calculation module is designed to be easily extensible for adding more technical indicators in the future.