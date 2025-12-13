from flask import Flask
from flask import render_template, redirect, request, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config
from search_course import search_course
from calculate_handicap import calculate_handicap

app = Flask(__name__)
app.secret_key = config.secret_key


@app.route("/")
def index():
    profile = {}
    rounds = None
    courses = None
    handicap = None

    if "username" in session:
        rows = db.query(
            "SELECT club, favorite_course FROM users WHERE username = ?",
            [session["username"]],
        )
        if rows:
            club, favorite_course = rows[0]
            profile = {"club": club, "favorite_course": favorite_course}

        user_id = db.get_user_id(session["username"])
        handicap = calculate_handicap(user_id)

        rows = db.query(
            "SELECT id, played_date, played_tee, played_strokes, holes FROM rounds WHERE user_id = ?",
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
        "index.html", profile=profile, rounds=rounds, courses=courses, handicap=handicap
    )


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/create_user", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    club = request.form["club"]
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
        sql = "INSERT INTO users (username, password_hash, club, favorite_course, handicap) VALUES (?, ?, ?, ?, ?)"
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
        return "Wrong username or password"
    password_hash = username_password_hash[0][0]

    if check_password_hash(password_hash, password):
        session["username"] = username
        return redirect("/")
    else:
        return "Wrong username or password"


@app.route("/logout")
def logout():
    session.clear()
    flash("You are logged out")
    return redirect("/")


@app.route("/update_profile", methods=["POST"])
def update_profile():
    club = request.form["club"]
    favorite = request.form["favorite_course"]
    row = db.query("SELECT id FROM users WHERE username = ?", [session["username"]])
    user_id = row[0][0]
    db.execute(
        "UPDATE users SET club = ?, favorite_course = ? WHERE id = ?",
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

    played_date = request.form["played_date"]
    tee = request.form["tee"]
    holes = request.form["holes"]
    strokes = request.form["strokes"]

    user_id = db.get_user_id(session["username"])

    sql = "INSERT INTO rounds (course_id, user_id, played_date, played_tee, played_strokes, holes) VALUES (?, ?, ?, ?, ?, ?)"
    db.execute(sql, [course_id, user_id, played_date, tee, strokes, holes])
    return redirect("/")


@app.route("/add_course", methods=["GET", "POST"])
def add_course():
    if request.method == "GET":
        return render_template("add_course.html")

    course_name = request.form["course_name"]
    par = request.form["par"]
    user_id = db.get_user_id(session["username"])

    sql = "INSERT INTO courses (user_id, name, par) VALUES (?, ?, ?)"
    db.execute(sql, [user_id, course_name, par])
    return redirect("/")


@app.route("/search")
def search():
    query = request.args.get("query")
    results = search_course(query) if query else []
    return render_template("search.html", query=query, results=results)


@app.route("/profile/<username>")
def profile(username):
    user_info = db.query(
        "SELECT club, favorite_course, handicap FROM users WHERE username = ?",
        [username],
    )
    user_id = db.get_user_id(username)
    rounds = db.get_player_rounds(user_id)

    own_profile = username == session["username"]

    club, favorite_course, handicap = user_info[0]
    print(rounds)
    return render_template(
        "profile.html",
        username=username,
        club=club,
        favorite_course=favorite_course,
        handicap=handicap,
        rounds=rounds,
        own_profile=own_profile,
    )


@app.route("/leaderboards")
def leaderboards():
    rows = db.query(
        """SELECT username, handicap, COUNT(rounds.id) as rounds_played, MAX(rounds.played_date) as last_active
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
        db.execute("DELETE FROM rounds WHERE id = ?", [round_id])
        return redirect("/")


@app.route("/edit_course/<int:course_id>", methods=["GET", "POST"])
def edit_course(course_id):
    if request.method == "GET":
        course = db.query("SELECT name, par FROM courses WHERE id = ?", [course_id])
        course = course[0]
        return render_template("edit.html", type="course", id=course_id, course=course)

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
        round = row[0]
        return render_template("edit.html", type="round", id=round_id, round=round)

    played_date = request.form["played_date"]
    played_tee = request.form["played_tee"]
    played_strokes = request.form["played_strokes"]
    holes = request.form["holes"]

    db.execute(
        "UPDATE rounds SET played_date = ?,played_tee = ?,played_strokes = ?, holes = ? WHERE id = ?",
        [played_date, played_tee, played_strokes, holes, round_id],
    )
    return redirect("/")
