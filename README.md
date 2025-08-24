# Stock Data Collector

A Python application to fetch, store, and analyze Chinese A-share stock market data using Tushare API.

## Features

- Fetch daily stock price data from Tushare API
- Store data in a local SQLite database
- Calculate technical indicators (MACD, RSI, KDJ)
- Easy to extend for additional indicators

## Project Structure

```
stock_data_collector/
├── .env.example              # Example environment variables file
├── main.py                   # Main entry point
├── config.py                 # Configuration settings
├── api/                      # API clients
│   └── tushare_client.py     # Tushare API client
├── data/                     # Data processing modules
│   └── data_fetcher.py       # Data fetching and storage orchestrator
├── database/                 # Database management
│   └── db_manager.py         # Database operations
├── scheduler/                # Scheduled tasks (currently empty)
├── utils/                    # Utility functions
│   └── indicator_calculator.py # Technical indicator calculation
└── test_indicators.py        # Test script for indicators
```

## Setup

1.  **Install Python:** Ensure you have Python 3.13.2 installed (as specified in `pyproject.toml`).
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    # Or if using uv:
    # uv pip install -r requirements.txt
    ```
3.  **Configure Environment Variables:**
    *   Copy `.env.example` to `.env`:
        ```bash
        cp .env.example .env
        ```
    *   Edit `.env` and replace `your_tushare_token_here` with your actual Tushare API token.

## Usage

Run the main script to fetch and store stock data along with calculated indicators:

```bash
python main.py
```

By default, it fetches data for the stock code `601818.SH` (China Everbright Bank) for the past 365 days. You can modify `config.py` to change the default stock code and date range, or modify `main.py` to fetch data for different stocks.

### Testing Indicators

You can test the indicator calculation functionality with the provided test script:

```bash
python test_indicators.py
```

## Technical Indicators

The application currently calculates the following technical indicators:

- **MACD** (Moving Average Convergence Divergence)
- **RSI14** (14-period Relative Strength Index) - Calculated using Wilder's Smoothing Method
- **KDJ** (Stochastic Oscillator) - Calculated using standard weighted moving average method

The indicator calculation module is designed to be easily extensible for adding more indicators in the future.