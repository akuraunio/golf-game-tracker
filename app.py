from flask import Flask
from flask import render_template, redirect, request, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create_user", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if len(password1) < 4:
        return "Error: Password needs to be atleast 4 characters"
    if password1 != password2:
        return "Error: passwords do not match"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "Error: Username is already taken"

    return "Account created"

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