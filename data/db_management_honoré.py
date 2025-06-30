import sqlite3

DB_PATH = "data.db"

def get_connection() :
    """
    open a connection to the SQlite data.db
    returns:
        SQlite connection object
    """
    return sqlite3.connect(DB_PATH)





