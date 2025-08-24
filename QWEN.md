# Qwen Code Context for `stock_data_collector`

## Project Overview

This is a Python application designed to collect and store historical stock market data for Chinese A-shares. It primarily uses the Tushare API to fetch daily price data for specified stocks and saves this data into a local SQLite database.

### Key Technologies & Libraries

*   **Python:** The core language of the application.
*   **Tushare:** The primary data source for stock market information.
*   **SQLite:** Used for local data storage.
*   **Requests:** (via `requirements.txt`) Likely used by Tushare internally or for other HTTP interactions.
*   **Pandas:** (via `requirements.txt`) Used for data manipulation and handling DataFrames.
*   **python-dotenv:** (via `requirements.txt`) Used to load configuration from a `.env` file.

### Architecture

The application follows a modular structure:

1.  **`main.py`**: The entry point. It initializes the fetching process for a default stock.
2.  **`config.py`**: Loads environment variables (like the Tushare token) and defines default settings (stock code, date range, database name).
3.  **`api/tushare_client.py`**: Wraps the Tushare Pro API, specifically providing a method to fetch daily stock price data.
4.  **`data/data_fetcher.py`**: Orchestrates the data fetching process. It calculates date ranges, checks the database for existing data, calls the Tushare client if needed, and passes the data to the database manager.
5.  **`database/db_manager.py`**: Handles all database interactions. It manages the SQLite connection, initializes the database schema, saves data, and checks for existing data to prevent duplicates.
6.  **`scheduler/` & **`utils/`**: Currently empty directories, likely intended for future features like scheduled data fetching and utility functions.

## Building and Running

1.  **Setup Environment:**
    *   Ensure Python 3.x is installed.
    *   Install dependencies: `pip install -r requirements.txt`.
    *   Copy `.env.example` to `.env` and add your Tushare API token: `cp .env.example .env` then edit `.env`.

2.  **Running the Application:**
    *   Execute the main script: `python main.py`.
    *   This will fetch data for the stock specified in `config.py` (`DEFAULT_STOCK_CODE`) for the last `DEFAULT_DAYS_BACK` days, provided it's not already in the database.

## Development Conventions

*   **Configuration:** Uses `python-dotenv` to manage sensitive information like API tokens via a `.env` file.
*   **Database:** Uses SQLite for simplicity. The schema is defined in `db_manager.py`. A `UNIQUE` constraint is used on `ts_code` and `trade_date` to prevent duplicate entries.
*   **Modularity:** Code is separated into distinct modules based on responsibility (API, Data, Database).
*   **Dependencies:** Managed via `requirements.txt`.