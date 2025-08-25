import sqlite3
from sqlite3 import Error
import pandas as pd

def create_connection(db_file):
    """ Create a database connection to the SQLite database specified by db_file """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_tables(conn):
    """ Create stock_data and indicators tables """
    try:
        cursor = conn.cursor()
        # Stock Data Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_data (
                stock_code TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                open REAL,
                close REAL,
                high REAL,
                low REAL REAL,
                volume REAL,
                PRIMARY KEY (stock_code, timestamp)
            );
        """)
        # Indicators Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS indicators (
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
        """)
        conn.commit()
    except Error as e:
        print(e)

def insert_stock_data(conn, stock_code, df):
    """ Insert stock data from a pandas DataFrame into the stock_data table """
    if df.empty:
        return

    # Ensure the DataFrame has the expected columns and index name
    df = df.copy()
    df['stock_code'] = stock_code
    df.index.name = 'timestamp'
    df = df.reset_index()

    # Convert datetime objects to string for SQLite
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Filter out columns that are not in the table schema
    df_to_insert = df[['stock_code', 'timestamp', 'open', 'close', 'high', 'low', 'volume']]

    try:
        df_to_insert.to_sql('stock_data', conn, if_exists='append', index=False, method='multi')
        print(f"Inserted/updated {len(df_to_insert)} rows for {stock_code} into stock_data.")
    except sqlite3.IntegrityError:
        # Handle cases where primary key already exists (e.g., update existing rows)
        # For simplicity, we'll just print a message. A more robust solution would involve
        # checking for existing data and performing an UPDATE or UPSERT.
        print(f"Some data for {stock_code} at {df_to_insert['timestamp'].min()} - {df_to_insert['timestamp'].max()} already exists. Skipping duplicates.")
    except Error as e:
        print(f"Error inserting stock data for {stock_code}: {e}")

def insert_indicator_data(conn, stock_code, timestamp, indicators_dict):
    """ Insert technical indicators data into the indicators table """
    try:
        cursor = conn.cursor()
        
        # Check if record exists
        cursor.execute("""
            SELECT 1 FROM indicators WHERE stock_code = ? AND timestamp = ?
        """, (stock_code, timestamp.strftime('%Y-%m-%d %H:%M:%S')))
        exists = cursor.fetchone()
        
        if exists:
            # Update existing record
            update_query = """
                UPDATE indicators SET
                MACD_DIF = COALESCE(?, MACD_DIF),
                MACD_DEA = COALESCE(?, MACD_DEA),
                MACD = COALESCE(?, MACD),
                RSI = COALESCE(?, RSI),
                KDJ_K = COALESCE(?, KDJ_K),
                KDJ_D = COALESCE(?, KDJ_D),
                KDJ_J = COALESCE(?, KDJ_J)
                WHERE stock_code = ? AND timestamp = ?
            """
            cursor.execute(update_query, (
                indicators_dict.get('MACD_DIF'),
                indicators_dict.get('MACD_DEA'),
                indicators_dict.get('MACD'),
                indicators_dict.get('RSI'),
                indicators_dict.get('KDJ_K'),
                indicators_dict.get('KDJ_D'),
                indicators_dict.get('KDJ_J'),
                stock_code,
                timestamp.strftime('%Y-%m-%d %H:%M:%S')
            ))
        else:
            # Insert new record
            insert_query = """
                INSERT INTO indicators (
                    stock_code, timestamp, MACD_DIF, MACD_DEA, MACD, 
                    RSI, KDJ_K, KDJ_D, KDJ_J
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (
                stock_code,
                timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                indicators_dict.get('MACD_DIF'),
                indicators_dict.get('MACD_DEA'),
                indicators_dict.get('MACD'),
                indicators_dict.get('RSI'),
                indicators_dict.get('KDJ_K'),
                indicators_dict.get('KDJ_D'),
                indicators_dict.get('KDJ_J')
            ))
        
        conn.commit()
    except Error as e:
        print(f"Error inserting indicator data for {stock_code}: {e}")

def get_stock_data(conn, stock_code, limit=None):
    """ Retrieve stock data for a given stock_code """
    try:
        query = f"SELECT timestamp, open, close, high, low, volume FROM stock_data WHERE stock_code = '{stock_code}' ORDER BY timestamp ASC"
        if limit:
            query += f" LIMIT {limit}"
        df = pd.read_sql_query(query, conn, parse_dates=['timestamp'], index_col='timestamp')
        return df
    except Error as e:
        print(f"Error retrieving stock data for {stock_code}: {e}")
        return pd.DataFrame()

if __name__ == '__main__':
    db_file = "test_stock_data.db"
    conn = create_connection(db_file)
    if conn:
        create_tables(conn)
        print("Database and tables created successfully.")

        # Example usage:
        # Dummy data for testing
        dummy_data = pd.DataFrame({
            'open': [10.0, 10.5, 11.0],
            'close': [10.4, 10.9, 11.5],
            'high': [10.6, 11.1, 11.7],
            'low': [9.9, 10.3, 10.8],
            'volume': [1000, 1200, 1100]
        }, index=pd.to_datetime(['2023-01-01 09:30:00', '2023-01-01 09:31:00', '2023-01-01 09:32:00']))

        insert_stock_data(conn, 'test_code', dummy_data)

        # Insert some indicator data
        insert_indicator_data(conn, 'test_code', pd.to_datetime('2023-01-01 09:32:00'), 'MACD', 0.5)

        # Retrieve data
        retrieved_df = get_stock_data(conn, 'test_code')
        print("\nRetrieved Stock Data:")
        print(retrieved_df)

        conn.close()
    else:
        print("Error! Cannot create the database connection.")
