import sqlite3

def sql_conn(db):
    # initialize my database connection
    conn = sqlite3.connect(db)
    # create a cursor
    cursor = conn.cursor()
    return conn, cursor
