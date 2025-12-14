CREATE TABLE clubs (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    club_id INTEGER NOT NULL REFERENCES clubs(id),
    favorite_course TEXT,
    handicap REAL NOT NULL
);

CREATE TABLE courses (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    club_id INTEGER NOT NULL REFERENCES clubs(id),
    name TEXT UNIQUE NOT NULL,
    par INTEGER NOT NULL
);

CREATE TABLE rounds (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
    played_date TEXT NOT NULL,
    played_tee TEXT NOT NULL,
    played_strokes INTEGER NOT NULL,
    holes INTEGER NOT NULL
);