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

## Development Conventions

*   **Dependencies:** Dependencies are managed via `pyproject.toml` and `requirements.txt`. The `uv.lock` file suggests `uv` might be the preferred package manager.
*   **Data Access:** The project supports multiple data sources (Tushare, Ashare). Ashare is self-contained in its directory.
*   **Technical Analysis:** The `MyTT` library provides a set of technical indicators compatible with common formula languages. It's designed to work with data fetched by libraries like Ashare.
*   **Submodules:** `Ashare` and `MyTT` are included as Git submodules, indicating they are separate, maintained projects integrated into this one.