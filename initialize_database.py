import sqlite3

con = sqlite3.connect("database.db")

with open("schema.sql") as schema:
    con.executescript(schema.read())

con.commit()
con.close()