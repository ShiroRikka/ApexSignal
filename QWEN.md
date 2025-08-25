# Stock Data Collector Project Context

## Project Overview

This project is a Python application designed to fetch, store, and analyze Chinese A-share stock market data. It primarily utilizes two data sources:

1.  **Tushare**: A professional financial data platform requiring an API token.
2.  **Ashare**: A lightweight, open-source API for real-time A-share market data, included as a submodule. It fetches data from sources like Sina Finance and Tencent Stock, providing automatic failover. It's designed for simplicity and portability.

The project also includes `MyTT`, a Python implementation of common technical analysis indicators (like MA, BOLL, MACD) originally found in platforms like Tongdaxin or Tushare's formula language. This is also included as a submodule.

Key files and directories:
*   `pyproject.toml`, `requirements.txt`: Define project dependencies (numpy, pandas, requests, tushare, akshare, baostock, python-dotenv).
*   `.env.example`: Template for storing the Tushare API token.
*   `Ashare/`: Submodule containing the Ashare API (`Ashare.py`) and demo scripts (`Demo1.py`, `Demo2.py`).
*   `MyTT/`: Submodule containing the MyTT technical analysis library (`MyTT.py`).

## Building and Running

This project is written in Python (requires Python >= 3.13 as per `pyproject.toml`).

1.  **Setup Environment:**
    *   Ensure Python 3.13+ is installed.
    *   It's recommended to use a virtual environment: `python -m venv venv` and activate it (`venv\Scripts\activate` on Windows).
    *   Install dependencies. You can use `pip install -r requirements.txt` or `uv` if preferred (as hinted by `uv.lock`).
2.  **Configuration:**
    *   Copy `.env.example` to `.env`.
    *   Edit `.env` and add your Tushare token if you plan to use the Tushare API.
3.  **Running Demos:**
    *   Navigate to the `Ashare` directory.
    *   Run the demo scripts to test data fetching: `python Demo1.py` or `python Demo2.py`. `Demo2.py` also demonstrates using `MyTT` for technical indicators and plotting.
4.  **Running Main Application:**
    *   Run `python main.py` to start the real-time data collection service. This will:
        *   Create a SQLite database (`stock_data.db`) if it doesn't exist.
        *   Fetch stock data at specified intervals (default: 1 minute).
        *   Calculate and store technical indicators.
        *   Monitor stock codes defined in `main.py` (currently set to '601818.SH' - Ping An Bank).

## Development Conventions

*   **Dependencies:** Dependencies are managed via `pyproject.toml` and `requirements.txt`. The `uv.lock` file suggests `uv` might be the preferred package manager.
*   **Data Access:** The project supports multiple data sources (Tushare, Ashare). Ashare is self-contained in its directory.
*   **Technical Analysis:** The `MyTT` library provides a set of technical indicators compatible with common formula languages. It's designed to work with data fetched by libraries like Ashare.
*   **Submodules:** `Ashare` and `MyTT` are included as Git submodules, indicating they are separate, maintained projects integrated into this one.
*   **Database:** Uses SQLite for data storage with two main tables:
    *   `stock_data`: Stores OHLCV (Open, High, Low, Close, Volume) data.
    *   `indicators`: Stores calculated technical indicator values.
*   **Configuration:** Environment variables are used for sensitive data like API tokens (Tushare).
*   **Code Structure:**
    *   `main.py`: Entry point for the real-time data collection service.
    *   `database_manager.py`: Handles all database operations (connection, table creation, data insertion/retrieval).
    *   `stock_data_processor.py`: Contains the core logic for fetching stock data and calculating technical indicators.
*   **Ignored Files:** The `.gitignore` file excludes virtual environments, environment files, IDE configurations, Python cache files, and database files from version control.

## Key Features

*   **Real-time Data Collection:** Continuously fetches stock market data at configurable intervals.
*   **Multiple Data Sources:** Supports both Tushare (professional) and Ashare (open-source) APIs.
*   **Technical Analysis:** Automatically calculates and stores common technical indicators (MACD, RSI, KDJ, etc.) using the MyTT library.
*   **Data Persistence:** Stores all collected data and calculated indicators in a SQLite database for historical analysis.
*   **Modular Design:** Clean separation of concerns between data fetching, processing, and storage.
*   **Easy Configuration:** Simple environment variable setup for API tokens.

## File Structure

```
stock_data_collector/
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore rules
├── database_manager.py      # Database operations
├── main.py                  # Main application entry point
├── pyproject.toml           # Project configuration and dependencies
├── QWEN.md                  # This context file
├── README.md                # Project documentation (empty)
├── requirements.txt         # Python dependencies
├── stock_data_processor.py  # Data fetching and processing logic
├── uv.lock                  # uv package manager lock file
├── Ashare/                  # Ashare API submodule
│   ├── Ashare.py           # Core Ashare API implementation
│   ├── Demo1.py            # Basic usage demo
│   ├── Demo2.py            # Advanced demo with MyTT integration
│   └── README.md           # Ashare documentation
└── MyTT/                    # MyTT technical analysis submodule
    ├── MyTT.py             # Core MyTT library
    ├── example1.py         # Usage examples
    └── README.md           # MyTT documentation
```