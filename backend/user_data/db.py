import sqlite3

conn = sqlite3.connect('databasesql.db')
cursor = conn.cursor()


def add_data(handle, id, curs, connection):
    curs.execute("""INSERT INTO USERS
    VALUES (?, ?)""", (handle, id))
    connection.commit()
