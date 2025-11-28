from flask import Flask
from flask import render_template, redirect, request, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config
from search_course import search_course

app = Flask(__name__)
app.secret_key = config.secret_key


@app.route("/")
def index():
    profile = {}
    rounds = None
    if "username" in session:
        rows = db.query(
            "SELECT club, favorite_course FROM users WHERE username = ?",
            [session["username"]],
        )
        if rows:
            club, favorite_course = rows[0]
            profile = {"club": club, "favorite_course": favorite_course}
        user_id = db.query(
            "SELECT id FROM users WHERE username = ?", [session["username"]]
        )
        user_id = user_id[0][0]
        rows = db.query(
            "SELECT course, played_date, played_tee, played_strokes, holes FROM rounds WHERE user_id = ?",
            [user_id],
        )
        if rows:
            rounds = rows
        else:
            rounds = None
    return render_template("index.html", profile=profile, rounds=rounds)


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


@app.route("/add_round_page")
def add_round_page():
    return render_template("add_round_page.html")


@app.route("/add_round", methods=["POST"])
def add_round():
    course = request.form["course"]
    played_date = request.form["played_date"]
    tee = request.form["tee"]
    holes = request.form["holes"]
    strokes = request.form["strokes"]
    par = request.form["par"]

    user_id = db.query("SELECT id FROM users WHERE username = ?", [session["username"]])
    user_id = user_id[0][0]

    sql = "INSERT INTO rounds (user_id, course, played_date, played_tee, played_strokes, holes, par) VALUES (?, ?, ?, ?, ?, ?, ?)"
    db.execute(sql, [user_id, course, played_date, tee, strokes, holes, par])
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

    club, favorite_course, handicap = user_info[0]
    return render_template(
        "profile.html",
        username=username,
        club=club,
        favorite_course=favorite_course,
        handicap=handicap,
    )
