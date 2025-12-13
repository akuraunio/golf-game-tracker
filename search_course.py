import db


def search_course(query):
    sql = "SELECT name, par FROM courses WHERE name LIKE ?"
    return db.query(sql, ["%" + query + "%"])
