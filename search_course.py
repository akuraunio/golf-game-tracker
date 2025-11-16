import db

def search_course(query):
    sql = """SELECT course, played_date, played_tee, played_strokes, holes FROM rounds WHERE course LIKE ?"""
    return db.query(sql, ["%" + query + "%"])