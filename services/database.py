import sqlite3

DB_PATH = 'messages.db'

def startDatabase():
    # Connects to the database if there is a file, if not creates it
    connection = sqlite3.connect(DB_PATH)
    # A tool to run SQL commands
    cursor = connection.cursor()
    # Runs the SQL command to create the table
    # IF NOT EXISTS makes it so that it doesn't recreate the table and crash
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS messages(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT NOT NULL,
                    incoming_message TEXT NOT NULL,
                    command TEXT,
                    response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                    ''')
    connection.commit()
    connection.close()

def saveMessageDatabase(phone_number, incoming_message, command=None, response=None):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('''
                    INSERT INTO messages (phone_number, incoming_message, command, response)
                    VALUES (?,?,?,?)
                    ''', (phone_number, incoming_message, command, response))
    connection.commit()
    connection.close()