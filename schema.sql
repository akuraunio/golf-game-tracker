CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    club TEXT,
    favorite_course TEXT,
    handicap REAL NOT NULL
);

CREATE TABLE courses (
    id INTEGER PRIMARY KEY
);

CREATE TABLE rounds (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    course TEXT NOT NULL,
    played_date TEXT NOT NULL,
    played_tee TEXT NOT NULL,
    played_strokes TEXT NOT NULL,
    holes INTEGER NOT NULL,
    par INTEGER NOT NULL
);