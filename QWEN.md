# Qwen Code Context for `stock_data_collector`

## Project Overview

This is a Python application named **Stock Data Collector**. Its primary purpose is to fetch, store, and potentially analyze Chinese A-share stock market data. It uses the **Tushare API** as the data source and stores the collected data in a **SQLite database**.

### Key Technologies

*   **Language:** Python (>= 3.13)
*   **Dependencies:** `pandas-stubs`, `python-dotenv`, `requests`, `tushare`
*   **Data Source:** Tushare API
*   **Database:** SQLite (`stock_data.db`)
*   **Environment Management:** `python-dotenv` (`.env` file)

### Architecture

The project follows a modular structure:

1.  **`api/tushare_client.py`**: Contains the `TushareClient` class, which wraps the Tushare Pro API calls, specifically for fetching daily stock price data.
2.  **`data/data_fetcher.py`**: Contains the `StockDataFetcher` class. This class orchestrates the process: it calculates the date range, checks if data already exists in the database (to avoid redundant API calls), calls the `TushareClient` to fetch data if needed, and then passes the data to the `DatabaseManager` for storage.
3.  **`database/db_manager.py`**: Contains the `DatabaseManager` class, responsible for all interactions with the SQLite database. It handles database initialization (creating tables) and saving/fetching data.
4.  **`config.py`**: Centralizes configuration settings, including loading the Tushare API token from environment variables (`.env`), database name, and default stock code/date range.
5.  **`main.py`** (Expected Entry Point): Although not found in the initial scan, this is likely the main script to run the application, as mentioned in the README. It would typically instantiate `StockDataFetcher` and trigger the data fetching process.
6.  **`scheduler/`** and **`utils/`**: Currently empty directories, intended for future scheduled tasks and utility functions, respectively.

## Building and Running

### Prerequisites

*   Python 3.13.2 (as specified in `pyproject.toml`)
*   A Tushare API token (obtained from the Tushare website)

### Setup

1.  **Install Dependencies:**
    *   Using `pip`:
        ```bash
        pip install -r requirements.txt
        ```
    *   Using `uv` (if preferred):
        ```bash
        uv pip install -r requirements.txt
        ```
2.  **Configure Environment Variables:**
    *   Copy the example environment file:
        ```bash
        cp .env.example .env # On Windows: copy .env.example .env
        ```
    *   Open the `.env` file and replace `your_tushare_token_here` with your actual Tushare API token.

### Running the Application

Based on the README, the primary command to run the application is:
```bash
python main.py
```
This command is expected to fetch and store stock data, using the default stock code (`601818.SH`) and date range (past 365 days) defined in `config.py`. You would modify `config.py` or `main.py` to change these parameters or fetch data for different stocks.

**Note:** The `main.py` file was not found in the scan. If it doesn't exist, the entry point might be different, or it needs to be created based on the logic in `data/data_fetcher.py`.

### Testing

There is no explicit testing framework or test commands found in the provided files (`pyproject.toml`, `requirements.txt`). Testing practices are not documented.

## Development Conventions

*   **Configuration:** Centralized in `config.py`, loaded from a `.env` file using `python-dotenv`.
*   **Modularity:** Code is split into distinct modules (`api`, `data`, `database`) with single-responsibility classes (`TushareClient`, `StockDataFetcher`, `DatabaseManager`).
*   **Database:** Uses SQLite with a clear table schema for `daily_price` data. Implements a basic check for existing data before inserting to prevent unnecessary API calls and potential duplicates (though the database `UNIQUE` constraint should handle duplicates on insertion).
*   **Dependencies:** Managed via `requirements.txt` and defined in `pyproject.toml`.