# Stock Data Collector

A Python application to fetch, store, and analyze Chinese A-share stock market data using Tushare API.

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
└── utils/                    # Utility functions (currently empty)
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

Run the main script to fetch and store stock data:

```bash
python main.py
```

By default, it fetches data for the stock code `601818.SH` (China Everbright Bank) for the past 365 days. You can modify `config.py` to change the default stock code and date range, or modify `main.py` to fetch data for different stocks.