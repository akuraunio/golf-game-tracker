import sqlite3
import secrets
from flask import Flask
from flask import abort, render_template, redirect, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config
from search_course import search_course
from calculate_handicap import calculate_handicap

app = Flask(__name__)
app.secret_key = config.SECRET_KEY


@app.route("/")
def index():
    user_profile = {}
    rounds = None
    courses = None
    handicap = None

    if "username" in session:
        rows = db.query(
            """
            SELECT clubs.name, users.favorite_course 
            FROM users JOIN clubs ON users.club_id=clubs.id
            WHERE users.username = ?""",
            [session["username"]],
        )
        if rows:
            club, favorite_course = rows[0]
            user_profile = {"club": club, "favorite_course": favorite_course}

        user_id = db.get_user_id(session["username"])
        handicap = calculate_handicap(user_id)

        rows = db.query(
            """SELECT id, played_date, played_tee, played_strokes, holes 
            FROM rounds WHERE user_id = ?""",
            [user_id],
        )
        if rows:
            rounds = rows
        else:
            rounds = None
        rows = db.query(
            "SELECT id, name, par FROM courses WHERE user_id = ?",
            [user_id],
        )
        if rows:
            courses = rows
        else:
            courses = None

    return render_template(
        "index.html",
        profile=user_profile,
        rounds=rounds,
        courses=courses,
        handicap=handicap,
    )


@app.route("/register")
def register():
    clubs = db.get_clubs()
    return render_template("register.html", clubs=clubs)


@app.route("/create_user", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    club_name = request.form["club_name"]
    club = db.get_club_id(club_name)
    print(club)
    favorite_course = request.form["favorite_course"]
    handicap = 54  # initial handicap is always 54

    if len(password1) < 4:
        flash("Error: Password needs to be atleast 4 characters")
        return redirect("/register")
    elif password1 != password2:
        flash("Error: passwords do not match")
        return redirect("/register")
    password_hash = generate_password_hash(password1)

    try:
        sql = """
        INSERT INTO users (username, password_hash, club_id, favorite_course, handicap) 
        VALUES (?, ?, ?, ?, ?)"""
        db.execute(sql, [username, password_hash, club, favorite_course, handicap])
    except sqlite3.IntegrityError:
        return "Error: Username is already taken"

    flash("Registration successful! You can login now")
    return redirect("/")


@app.route("/login", methods=["POST", "GET"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    sql = "SELECT password_hash FROM users WHERE username = ?"
    username_password_hash = db.query(sql, [username])
    if not username_password_hash:
        flash("Wrong username or password")
        return redirect("/")
    password_hash = username_password_hash[0][0]

    if check_password_hash(password_hash, password):
        session["username"] = username
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")
    else:
        flash("Wrong username or password")
        return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    flash("You are logged out")
    return redirect("/")


@app.route("/update_profile", methods=["POST"])
def update_profile():
    check_csrf()
    club_name = request.form["club_name"]
    club = db.get_club_id(club_name)
    favorite = request.form["favorite_course"]
    row = db.query("SELECT id FROM users WHERE username = ?", [session["username"]])
    user_id = row[0][0]
    db.execute(
        "UPDATE users SET club_id = ?, favorite_course = ? WHERE id = ?",
        [club if club else None, favorite if favorite else None, user_id],
    )
    return redirect("/")


@app.route("/add_round/<int:course_id>", methods=["GET", "POST"])
def add_round(course_id):
    if request.method == "GET":
        course = db.query("SELECT name FROM Courses WHERE id = ?", [course_id])
        course_name = course[0][0]
        return render_template(
            "add_round.html", course_id=course_id, course_name=course_name
        )

    check_csrf()
    played_date = request.form["played_date"]
    tee = request.form["tee"]
    holes = request.form["holes"]
    strokes = request.form["strokes"]

    if int(strokes) <= 0:
        flash("Error: strokes must be greater than 0")
        return redirect(request.url)
    elif int(strokes) < int(holes):
        flash("Error: strokes must be equal or greater than holes played")
        return redirect(request.url)

    user_id = db.get_user_id(session["username"])

    sql = """
    INSERT INTO rounds (course_id, user_id, played_date, played_tee, played_strokes, holes) 
    VALUES (?, ?, ?, ?, ?, ?)
    """
    db.execute(sql, [course_id, user_id, played_date, tee, strokes, holes])
    return redirect("/")


@app.route("/add_course", methods=["GET", "POST"])
def add_course():
    if request.method == "GET":
        clubs = db.get_clubs()
        return render_template("add_course.html", clubs=clubs)

    check_csrf()
    course_name = request.form["course_name"]
    par = request.form["par"]
    club_name = request.form["club_name"]
    club = db.get_club_id(club_name)

    user_id = db.get_user_id(session["username"])

    sql = "INSERT INTO courses (user_id, club_id, name, par) VALUES (?, ?, ?, ?)"
    db.execute(sql, [user_id, club, course_name, par])
    return redirect("/")


@app.route("/search")
def search():
    query = request.args.get("query")
    results = search_course(query) if query else []
    return render_template("search.html", query=query, results=results)


@app.route("/profile/<username>")
def profile(username):
    user_info = db.query(
        """
            SELECT clubs.name, users.favorite_course, users.handicap 
            FROM users JOIN clubs ON users.club_id=clubs.id
            WHERE users.username = ?""",
        [username],
    )
    user_id = db.get_user_id(username)
    rounds = db.get_player_rounds(user_id)
    clubs = db.get_clubs()

    own_profile = username == session["username"]

    club, favorite_course, handicap = user_info[0]
    print(rounds)
    return render_template(
        "profile.html",
        username=username,
        user_club=club,
        clubs=clubs,
        favorite_course=favorite_course,
        handicap=handicap,
        rounds=rounds,
        own_profile=own_profile,
    )


@app.route("/leaderboards")
def leaderboards():
    rows = db.query(
        """SELECT username, handicap, 
        COUNT(rounds.id) as rounds_played, MAX(rounds.played_date) as last_active
        FROM users
        LEFT JOIN rounds ON users.id=rounds.user_id
        GROUP BY users.id
        ORDER BY handicap ASC 
        LIMIT 10"""
    )

    return render_template("leaderboards.html", users=rows)


@app.route("/delete_course/<int:course_id>", methods=["GET", "POST"])
def delete_course(course_id):

    if request.method == "GET":
        course_name = db.get_course_name(course_id)
        return render_template(
            "delete.html", name=course_name, type="course", id=course_id
        )

    else:
        check_csrf()
        db.execute("DELETE FROM courses WHERE id = ?", [course_id])
        return redirect("/")


@app.route("/delete_round/<int:round_id>", methods=["GET", "POST"])
def delete_round(round_id):
    if request.method == "GET":
        round_name = db.query("SELECT played_date FROM rounds WHERE id = ?", [round_id])
        round_name = "played on " + round_name[0][0]
        return render_template(
            "delete.html", name=round_name, type="round", id=round_id
        )

    else:
        check_csrf()
        db.execute("DELETE FROM rounds WHERE id = ?", [round_id])
        return redirect("/")


@app.route("/edit_course/<int:course_id>", methods=["GET", "POST"])
def edit_course(course_id):
    if request.method == "GET":
        course = db.query("SELECT name, par FROM courses WHERE id = ?", [course_id])
        course = course[0]
        return render_template("edit.html", type="course", id=course_id, course=course)

    check_csrf()
    course_name = request.form["name"]
    par = request.form["par"]

    db.execute(
        "UPDATE courses SET name = ?, par = ? WHERE id = ?",
        [course_name, par, course_id],
    )
    return redirect("/")


@app.route("/edit_round/<int:round_id>", methods=["GET", "POST"])
def edit_round(round_id):
    if request.method == "GET":
        row = db.query(
            "SELECT played_date, played_tee, played_strokes, holes FROM rounds WHERE id=?",
            [round_id],
        )
        golf_round = row[0]
        return render_template("edit.html", type="round", id=round_id, round=golf_round)

    check_csrf()
    played_date = request.form["played_date"]
    played_tee = request.form["played_tee"]
    played_strokes = request.form["played_strokes"]
    holes = request.form["holes"]

    db.execute(
        """
        UPDATE rounds SET played_date = ?,played_tee = ?,played_strokes = ?, holes = ? 
        WHERE id = ?
        """,
        [played_date, played_tee, played_strokes, holes, round_id],
    )
    return redirect("/")


def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)
