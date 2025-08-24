# Stock Data Collector - Project Context

## Project Overview

This is a Python application designed to fetch, store, and potentially analyze Chinese A-share stock market data. It primarily uses the Tushare API to retrieve historical stock price information and stores this data in a local SQLite database.

### Core Technologies

*   **Language:** Python (>= 3.13)
*   **API:** Tushare Pro API for stock data.
*   **Data Processing:** `pandas`
*   **Database:** SQLite (`stock_data.db`)
*   **Dependencies:** Managed via `requirements.txt` or `pyproject.toml` (using `pandas-stubs`, `python-dotenv`, `requests`, `tushare`).

### Architecture

The project is structured into several modules:

1.  **`main.py`**: The main entry point. It parses command-line arguments (stock code, date range) and initiates the data fetching process.
2.  **`config.py`**: Loads environment variables (like the Tushare API token) and defines default settings (database name, default stock code, default date range).
3.  **`api/tushare_client.py`**: Contains the `TushareClient` class, which wraps the Tushare Pro API calls, specifically for fetching daily stock price data.
4.  **`data/data_fetcher.py`**: Contains the `StockDataFetcher` class. This class orchestrates the workflow: it uses `TushareClient` to get data, checks the database for existing data using `DatabaseManager`, and then saves the new data if needed.
5.  **`database/db_manager.py`**: Contains the `DatabaseManager` class. It handles all interactions with the SQLite database, including initializing tables (`daily_price`) and saving/fetching data.
6.  **`scheduler/`**: An empty directory, likely intended for future scheduled task implementations (e.g., using `cron` or `APScheduler`).
7.  **`utils/`**: An empty directory, likely intended for utility functions.
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
3.  **Database:** The application automatically creates a SQLite database file named `stock_data.db` in the project root if it doesn't exist. It will create a `daily_price` table to store the fetched data.

## Development Conventions

*   **Configuration:** Sensitive settings like API tokens are managed via environment variables loaded using `python-dotenv`. The `.env` file is not committed to version control (as per `.gitignore`).
*   **Dependencies:** Dependencies are listed in `requirements.txt` and defined in `pyproject.toml`.
*   **Module Structure:** Code is organized into modules (`api`, `data`, `database`) to separate concerns.
*   **Error Handling:** Basic error handling is implemented in API calls and database operations, printing error messages to the console.
*   **Future Work:** The `scheduler` and `utils` directories are placeholders for future enhancements, such as automated data fetching and common utility functions.