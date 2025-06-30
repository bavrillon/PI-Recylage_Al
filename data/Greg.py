import sqlite3

conn = sqlite3.connect('data.db')

def get_connection():
    """
    Open a connection to the SQLite data.db
    returns:
        SQLite connection object
    """
    return conn
cursor = conn.cursor()