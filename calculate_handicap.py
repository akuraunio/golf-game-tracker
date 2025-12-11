import db


def calculate_handicap(user_id):
    # calculate handicap based on the last 5 or fewer played rounds
    sql = """
    SELECT courses.par, rounds.holes, rounds.played_strokes
    FROM rounds JOIN courses ON rounds.course_id = courses.id
    WHERE rounds.user_id = ?
    ORDER BY rounds.played_date DESC
    LIMIT 5
"""
    handicap_rounds = db.query(sql, [user_id])

    if not handicap_rounds:
        return 54

    differentials = []

    for par, holes, strokes in handicap_rounds:
        # scale 9 hole round to 18 hole round
        par, holes, strokes = int(par), int(holes), int(strokes)
        if holes == 9:
            par *= 2
            strokes *= 2

        differential = strokes - par
        differentials.append(differential)

    handicap_index = round((sum(differentials) / len(differentials)) * 0.96, 1)

    db.execute("UPDATE users SET handicap = ? WHERE id = ?", [handicap_index, user_id])

    return handicap_index


def get_handicap(user_id):
    sql = """
    SELECT handicap
    FROM users
    WHERE user_id = ?
"""
    handicap = db.query(sql, [user_id])
    return handicap[0][0]
