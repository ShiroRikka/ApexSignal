# Project Overview

This project, "stock-data-collector", is a Python application designed to fetch, store, and analyze Chinese A-share stock market data. It leverages various APIs such as Tushare, Ashare, Akshare, and Baostock to collect data and includes a comprehensive library (`MyTT`) for technical analysis indicators.

**Key Technologies:**
*   **Python:** The primary programming language.
*   **Data Acquisition:** Ashare (Tencent, Sina APIs), Tushare, Akshare, Baostock.
*   **Data Manipulation:** Pandas, NumPy.
*   **Technical Analysis:** MyTT library (implementation of various stock indicators).
*   **Environment Management:** `uv` (indicated by `uv.lock`).

**Architecture:**
The project appears to be structured with separate modules for data acquisition (`Ashare/Ashare.py`) and technical analysis (`MyTT/MyTT.py`). Data fetching functions are designed to retrieve historical stock data at various frequencies (daily, weekly, monthly, minute-level). The `MyTT` library provides a wide array of financial indicators for market analysis.

# Building and Running

This project uses `uv` for dependency management.

**Installation:**
1.  Ensure you have `uv` installed. If not, you can install it via `pip`:
    ```bash
    pip install uv
    ```
2.  Install the project dependencies:
    ```bash
    uv sync
    ```

**Running:**
Specific run commands are not explicitly defined in the `pyproject.toml` or other analyzed files. However, based on the structure, you would typically run individual Python scripts.

*   **Example (Ashare data fetching):**
    ```bash
    python Ashare/Ashare.py
    ```
    (Note: The `if __name__ == '__main__':` block in `Ashare.py` demonstrates basic usage.)

*   **Example (MyTT usage):**
    You would typically import and use functions from `MyTT.py` within your own analysis scripts.

# Development Conventions

*   **Dependencies:** Managed via `pyproject.toml` and `requirements.txt` (for `uv` or `pip`).
*   **Code Style:** Pythonic, with a focus on clear function definitions for data retrieval and technical indicators.
*   **Data Handling:** Extensive use of Pandas DataFrames for data manipulation and analysis.
*   **API Keys:** It is highly probable that API keys for services like Tushare will be required and should be managed via environment variables (e.g., in a `.env` file, as suggested by `.env.example`).
