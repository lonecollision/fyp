import sqlite3
# open connection with database file named database.db (created once ran)
connection = sqlite3.connect('database.db')

# open schema.sql file
with open('schema.sql') as f:
    # execute sql script on connection to database.db
    connection.executescript(f.read())
# cursor allows you to execute sqlite commands in the connection
cur = connection.cursor()

# cinnut any pending transactions which belong to any cursor in the program
connection.commit()
# close connection
connection.close()