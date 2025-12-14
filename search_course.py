import db


def search_course(query):
    sql = """
            SELECT
                courses.id,
                courses.name,
                courses.par,
                clubs.name AS club_name,
                users.username AS username
            FROM courses
            JOIN users ON courses.user_id = users.id
            JOIN clubs ON users.club_id = clubs.id
            WHERE courses.name LIKE ?
            """
    return db.query(sql, ["%" + query + "%"])
