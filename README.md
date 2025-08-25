# Stock Data Collector

A Python application to fetch, store, and analyze Chinese A-share stock market data using Tushare or Ashare APIs.

## Features

- Fetch daily stock price data from Tushare API using the powerful `pro_bar` interface (with forward adjusted prices for accurate technical analysis)
- Fetch daily stock price data from Ashare API (alternative data source, based on [mpquant/Ashare](https://github.com/mpquant/Ashare))
- Store data in a local SQLite database
- Calculate technical indicators (MACD, RSI14, KDJ)
- Easy to extend for additional indicators

## Project Structure

```
stock_data_collector/
├── .env.example              # Example environment variables file
├── main.py                   # Main entry point
├── config.py                 # Configuration settings
├── api/                      # API clients
│   ├── tushare_client.py     # Tushare API client using pro_bar interface
│   └── ashare_client.py      # Ashare API client (based on mpquant/Ashare)
├── data/                     # Data processing modules
│   ├── data_fetcher.py       # Data fetching and storage orchestrator (Tushare)
│   └── ashare_data_fetcher.py # Data fetching and storage orchestrator (Ashare)
├── database/                 # Database management
│   └── db_manager.py         # Database operations
├── scheduler/                # Scheduled tasks (currently empty)
├── utils/                    # Utility functions
│   ├── indicator_calculator.py # Technical indicator calculation
│   └── code_converter.py     # Code format conversion utilities
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

By default, it fetches data for the stock code `601818.SH` (China Everbright Bank) for the past 365 days using Tushare API. You can modify `config.py` to change the default stock code and date range, or modify `main.py` to fetch data for different stocks.

### Using Ashare API

To use Ashare API instead of Tushare API, use the `--api` argument:

```bash
python main.py --api ashare
```

### Testing Indicators

You can test the indicator calculation functionality with the provided test script:

```bash
python test_indicators.py
```

## Technical Indicators

The application currently calculates the following technical indicators:

- **MACD** (Moving Average Convergence Divergence) - Standard implementation with DIF line (fast line), DEA line (slow/signal line), and MACD bar (histogram)
- **RSI14** (14-period Relative Strength Index) - Calculated using Wilder's Smoothing Method
- **KDJ** (Stochastic Oscillator) - Calculated using standard weighted moving average method

The indicator calculation module is designed to be easily extensible for adding more indicators in the future.