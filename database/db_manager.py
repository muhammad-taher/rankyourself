import mysql.connector
from mysql.connector import Error
from config import Config

def get_db_connection():
    """
    Establishes a connection to the MySQL database.
    Returns the connection object.
    """
    try:
        if not Config.DB_HOST or Config.DB_HOST == 'localhost' and os.environ.get('VERCEL'):
            print("ERROR: Vercel cannot connect to 'localhost'. Please set a remote DB_HOST in Vercel settings.")
            return None

        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT,
            connect_timeout=5 # Fail fast on serverless
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def execute_query(query, params=None, commit=False):
    """
    Executes a raw SQL query safely using parameterized queries.
    - query: SQL string with %s placeholders.
    - params: Tuple of parameters.
    - commit: Set to True for INSERT/UPDATE/DELETE.
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    cursor = connection.cursor(dictionary=True)
    result = None
    
    try:
        cursor.execute(query, params or ())
        if commit:
            connection.commit()
            result = cursor.lastrowid
        else:
            result = cursor.fetchall()
    except Error as e:
        print(f"Query Error: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()
        
    return result
