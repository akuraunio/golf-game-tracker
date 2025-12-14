import sqlite3

con = sqlite3.connect("database.db")

with open("schema.sql") as schema:
    con.executescript(schema.read())

clubs = [
    "Safrvik Golfklubi",
    "Pickala Golf Club",
    "Kurk Golf",
    "Tapiola Golf",
    "Espoo Ringside Golf",
    "Karelia Golf",
    "Levi Golf",
    "Tawast Golf",
]

con.executemany("INSERT INTO clubs (name) VALUES (?)", clubs)

con.commit()
con.close()
