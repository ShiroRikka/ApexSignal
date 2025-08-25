# Stock Data Collector Project

## Project Overview

This is a Python application designed to fetch, store, and analyze Chinese A-share stock market data. The project provides a comprehensive solution for collecting historical and real-time stock data, calculating technical indicators, and storing everything in a structured SQLite database.

### Key Features
- **Historical Data Collection**: Fetches daily historical stock data (default: 59 days) for specified stocks
- **Real-time Monitoring**: Continuously monitors stocks with configurable polling intervals (default: 60 seconds)
- **Technical Analysis**: Calculates and stores popular technical indicators including MACD, RSI, and KDJ
- **Data Persistence**: Uses SQLite database with proper schema for stock data and indicators
- **Multiple API Support**: Integrates with Tushare and Ashare APIs for data fetching

### Architecture
The project follows a modular architecture with clear separation of concerns:
- `main.py`: Entry point and orchestration logic
- `database_manager.py`: Database operations and schema management
- `stock_data_processor.py`: Data fetching and technical indicator calculations
- `Ashare/`: Third-party library for Chinese stock market data (git-ignored)
- `MyTT/`: Technical analysis library for calculating indicators (git-ignored)

## Technologies Used

### Core Dependencies
- **Python 3.13+**: Main programming language
- **SQLite**: Database for data persistence
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing support

### External APIs & Libraries
- **Tushare (>=1.4.23)**: Chinese financial data API
- **Ashare**: Custom library for A-share data fetching
- **MyTT**: Technical analysis library for Chinese stock market
- **akshare (>=1.17.41)**: Alternative data source
- **baostock (>=0.8.9)**: Additional data source option

### Utilities
- **python-dotenv (>=1.1.1)**: Environment variable management
- **requests (>=2.32.5)**: HTTP client for API calls

## Building and Running

### Prerequisites
- Python 3.13 or higher
- Package manager (uv recommended, pip also supported)

### Setup
1. **Install dependencies**:
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   - Copy `.env.example` to `.env`
   - Add your Tushare API token:
     ```
     TUSHARE_TOKEN=your_actual_tushare_token_here
     ```

### Running the Application
```bash
python main.py
```

The application will:
1. Initialize the SQLite database (`stock_data.db`)
2. Create necessary tables if they don't exist
3. Fetch 59 days of historical data for configured stocks
4. Start real-time monitoring with 60-second intervals
5. Calculate and store technical indicators

### Default Configuration
- **Stock Codes**: Currently monitors `sh601818` (Ping An Bank)
- **Historical Data**: 1 year (approximately 250 trading days) of daily data
- **Real-time Frequency**: 1-minute intraday data
- **Polling Interval**: 60 seconds
- **Database**: `stock_data.db` (SQLite)

## Development Conventions

### Code Structure
- **Modular Design**: Each module has a single responsibility
- **Database First**: SQLite schema is defined in `database_manager.py`
- **Error Handling**: Comprehensive try-catch blocks with meaningful error messages
- **Data Validation**: Checks for empty DataFrames and None API responses

### Database Schema
The application uses two main tables:

#### stock_data table
```sql
CREATE TABLE stock_data (
    stock_code TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    open REAL,
    close REAL,
    high REAL,
    low REAL,
    volume REAL,
    PRIMARY KEY (stock_code, timestamp)
);
```

#### indicators table
```sql
CREATE TABLE indicators (
    stock_code TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    MACD_DIF REAL,
    MACD_DEA REAL,
    MACD REAL,
    RSI REAL,
    KDJ_K REAL,
    KDJ_D REAL,
    KDJ_J REAL,
    PRIMARY KEY (stock_code, timestamp),
    FOREIGN KEY (stock_code, timestamp) REFERENCES stock_data (stock_code, timestamp)
);
```

### Technical Indicators
The project calculates and stores the following technical indicators:
- **MACD**: Moving Average Convergence Divergence (DIF, DEA, MACD histogram)
- **RSI**: Relative Strength Index (14-period)
- **KDJ**: Stochastic Oscillator (K, D, J lines)

### Data Flow
1. **Initialization**: Fetch 1 year of historical daily data for all monitored stocks
2. **Real-time Loop**:
   - Fetch latest intraday data point
   - Combine with historical data
   - Recalculate all technical indicators
   - Store latest indicator values
   - Wait for next polling interval

### Error Handling
- API failures are caught and logged without crashing the application
- Database integrity errors are handled gracefully
- Empty or None data responses are checked before processing

### Testing
The project includes test code in `__main__` blocks for standalone testing of individual modules:
- `database_manager.py`: Test database creation and data insertion
- `stock_data_processor.py`: Test data fetching and indicator calculation

## Configuration Notes

### Environment Variables
- `TUSHARE_TOKEN`: Required for Tushare API access
- The application can work with Ashare API without additional configuration

### Customization
To monitor different stocks or change settings:
1. Modify the `stock_codes` list in `main.py`
2. Adjust `intraday_frequency` and `polling_interval` as needed
3. Change the historical data `count` parameter (default: 250 trading days ≈ 1 year)

### Database Management
- The database file `stock_data.db` is created automatically
- Tables are created if they don't exist on application start
- Data insertion handles duplicates gracefully with upsert logic