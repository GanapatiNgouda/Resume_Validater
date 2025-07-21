import pyodbc
from config import settings

def get_db_connection():
    """
    Establishes a connection to the MSSQL database and yields the connection object.
    Ensures the connection is closed after use.
    """
    conn = None
    try:
        conn_str = (
            f"DRIVER={settings.DB_DRIVER};"
            f"SERVER={settings.DB_SERVER},{settings.DB_PORT};"
            f"DATABASE={settings.DB_DATABASE};"
            f"UID={settings.DB_USERNAME};"
            f"PWD={settings.DB_PASSWORD};"
            f"Trusted_Connection=yes;"
        )
        print(conn_str)
        conn = pyodbc.connect(conn_str)
        yield conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        # Handle specific connection errors here if needed
        print(f"Database connection error: {sqlstate} - {ex.args[1]}")
        raise
    finally:
        if conn:
            conn.close()

def execute_query(conn: pyodbc.Connection, query: str, params: tuple = None):
    """
    Executes a SQL query and returns the results.
    """
    cursor = conn.cursor()
    cursor.execute(query, params if params else ())

    return cursor.fetchall()

def execute_non_query(conn: pyodbc.Connection, query: str, params: tuple = None):
    """
    Executes a SQL query that does not return results (e.g., INSERT, UPDATE, DELETE).
    """
    cursor = conn.cursor()
    cursor.execute(query, params if params else ())
    conn.commit()
    return cursor.rowcount # Returns number of rows affected