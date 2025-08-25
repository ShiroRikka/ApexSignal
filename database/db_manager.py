"""Database manager for storing and retrieving stock data."""

import sqlite3
from config import DB_NAME

class DatabaseManager:
    """Manages database connections and operations for stock data."""

    def __init__(self, db_name=DB_NAME):
        """Initialize the database manager with the database name."""
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        """Get a new database connection."""
        return sqlite3.connect(self.db_name)

    def init_db(self):
        """Initialize the database, creating table structures if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create daily price data table for Tushare
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_price_tushare (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts_code TEXT,
                trade_date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                vol REAL,
                amount REAL,
                UNIQUE(ts_code, trade_date)
            )
        ''')

        # Create daily price data table for Ashare
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_price_ashare (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts_code TEXT,
                trade_date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                vol REAL,
                amount REAL,
                UNIQUE(ts_code, trade_date)
            )
        ''')

        # Create indicators table for Tushare
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS indicators_tushare (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts_code TEXT,
                trade_date TEXT,
                macd_dif REAL,
                macd_dea REAL,
                macd_bar REAL,
                rsi REAL,
                kdj_k REAL,
                kdj_d REAL,
                kdj_j REAL,
                UNIQUE(ts_code, trade_date)
            )
        ''')

        # Create indicators table for Ashare
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS indicators_ashare (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts_code TEXT,
                trade_date TEXT,
                macd_dif REAL,
                macd_dea REAL,
                macd_bar REAL,
                rsi REAL,
                kdj_k REAL,
                kdj_d REAL,
                kdj_j REAL,
                UNIQUE(ts_code, trade_date)
            )
        ''')

        conn.commit()
        conn.close()
        print(f"Database {self.db_name} initialized with separate tables for each data source.")

    def save_daily_price_data(self, df_daily, source='tushare'):
        """
        Save daily price data to the database.

        Args:
            df_daily (pandas.DataFrame): DataFrame containing daily price data.
            source (str): Data source ('tushare' or 'ashare').
        """
        if df_daily is None or df_daily.empty:
            print("No daily price data to save.")
            return

        table_name = f"daily_price_{source}"
        conn = self.get_connection()
        try:
            # Use 'append' mode with UNIQUE constraint to avoid duplicates
            df_daily.to_sql(table_name, conn, if_exists='append', index=False)
            print(f"Successfully saved {len(df_daily)} daily price records to the {table_name} table.")
        except Exception as e:
            # This might catch duplicate data errors, which can be handled or ignored
            print(f"Error saving daily price data to {table_name} table (may contain duplicates): {e}")
        finally:
            conn.close()

    def save_indicators_data(self, df_indicators, source='tushare'):
        """
        Save indicators data to the database.

        Args:
            df_indicators (pandas.DataFrame): DataFrame containing indicators data.
            source (str): Data source ('tushare' or 'ashare').
        """
        if df_indicators is None or df_indicators.empty:
            print("No indicators data to save.")
            return

        # Select only the columns needed for the indicators table
        indicators_columns = [
            'ts_code', 'trade_date', 'macd_dif', 'macd_dea', 
            'macd_bar', 'rsi', 'kdj_k', 'kdj_d', 'kdj_j'
        ]
        
        # Check if all required columns exist in the DataFrame
        missing_columns = set(indicators_columns) - set(df_indicators.columns)
        if missing_columns:
            print(f"Missing columns in indicators data: {missing_columns}")
            return
        
        df_to_save = df_indicators[indicators_columns]
        table_name = f"indicators_{source}"

        conn = self.get_connection()
        try:
            # Use 'append' mode with UNIQUE constraint to avoid duplicates
            df_to_save.to_sql(table_name, conn, if_exists='append', index=False)
            print(f"Successfully saved {len(df_to_save)} indicators records to the {table_name} table.")
        except Exception as e:
            # This might catch duplicate data errors, which can be handled or ignored
            print(f"Error saving indicators data to {table_name} table (may contain duplicates): {e}")
        finally:
            conn.close()

    def check_data_exists(self, table_name, ts_code, start_date=None, end_date=None):
        """
        Check if specific data already exists in the database.

        For the 'daily_price' tables, checks for data of a specific stock and date range.

        Args:
            table_name (str): The name of the table to check.
            ts_code (str): The stock code.
            start_date (str, optional): The start date in 'YYYYMMDD' format.
            end_date (str, optional): The end date in 'YYYYMMDD' format.

        Returns:
            bool: True if data exists, False otherwise.
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        if table_name in ['daily_price_tushare', 'daily_price_ashare']:
            if start_date and end_date:
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {table_name} 
                    WHERE ts_code = ? AND trade_date BETWEEN ? AND ?
                """, (ts_code, start_date, end_date))
                count = cursor.fetchone()[0]
                # Simple check: if at least one record exists, consider data present
                exists = count > 0
            else:
                cursor.execute(f"SELECT 1 FROM {table_name} WHERE ts_code = ?", (ts_code,))
                exists = cursor.fetchone() is not None
        else:
            exists = False

        conn.close()
        return exists

    def get_latest_data(self, base_table_name, source, ts_code, limit=5):
        """
        Get the latest data records for a specific stock from a table.

        Args:
            base_table_name (str): The base name of the table to query ('daily_price' or 'indicators').
            source (str): Data source ('tushare' or 'ashare').
            ts_code (str): The stock code.
            limit (int): The number of latest records to retrieve.

        Returns:
            list: A list of tuples containing the latest records.
        """
        table_name = f"{base_table_name}_{source}"
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT * FROM {table_name}
            WHERE ts_code = ?
            ORDER BY trade_date DESC
            LIMIT ?
        """, (ts_code, limit))
        
        records = cursor.fetchall()
        conn.close()
        return records

    def get_supported_sources(self):
        """
        Get a list of supported data sources.
        
        Returns:
            list: A list of supported data sources.
        """
        return ['tushare', 'ashare']