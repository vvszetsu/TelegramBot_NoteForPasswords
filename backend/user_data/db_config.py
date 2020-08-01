import sqlite3

conn = sqlite3.connect('databasesql.db')
cursor = conn.cursor()
conn.execute("""DROP TABLE IF EXISTS USERS""")
conn.execute("""CREATE TABLE IF NOT EXISTS USERS (handle TEXT, chat_id INT, superlogin_hash TEXT,
                last_auth_time TEXT) """)