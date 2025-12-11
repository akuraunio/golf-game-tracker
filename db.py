import sqlite3
from flask import g


def get_connection():
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con


def execute(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid
    con.close()


def last_insert_id():
    return g.last_insert_id


def query(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result


def get_user_id(username):
    user_id = query("SELECT id FROM users WHERE username = ?", [username])
    return user_id[0][0]


def get_player_rounds(user_id):
    sql = """
        SELECT
            rounds.id,
            rounds.played_date,
            rounds.holes,
            rounds.played_tee,
            rounds.played_strokes,
            courses.name
        FROM rounds
        JOIN courses ON rounds.course_id = courses.id
        WHERE rounds.user_id = ?
        ORDER BY rounds.played_date DESC
    """
    rows = query(sql, [user_id])
    return rows


def get_course_name(course_id):
    course_name = query("SELECT name FROM courses WHERE id = ?", [course_id])
    if not course_name:
        return None
    else:
        return course_name[0][0]
