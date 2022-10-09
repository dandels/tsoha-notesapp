from os import getenv
from flask import Flask, flash, session, redirect, render_template, request
from db import Db
from dotenv import load_dotenv

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
load_dotenv()
app.secret_key = getenv("APP_SECRET_KEY")
db = Db(app)


@app.route("/")
def root():
    return redirect("index.html")


@app.route("/index.html")
def index():
    return render_template("index.html")


@app.route("/notes.html", methods=["GET", "POST"])
def notes():
    if "user_id" not in session:
        return redirect("login.html")

    if request.method == "POST":
        if db.post_note(request.form["new-note"]):
            print("Posted note succesfully")
        else:
            print("Unable to post note")
    notes = db.get_notes()
    return render_template("notes.html", notes=notes)


@app.route("/todo.html")
def todo():
    if "user_id" not in session:
        return redirect("login.html")
    return render_template("todo.html")


@app.route("/login.html", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if db.try_login(request.form["username"], request.form["password"]):
            session["user_id"] = db.user_id_for(request.form["username"])
            return redirect("/")
        else:
            # TODO show error message
            print("Invalid login")
    return render_template("login.html")


@app.route("/register.html", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("/register.html")
    if request.method == "POST":
        can_register = db.try_register(
                request.form["username"],
                request.form["password"]
                )
        if can_register:
            # TODO log in and register user
            print("succesfully registered")
            return redirect("/index.html")
        else:
            flash("Username not available.", category="error")
        return render_template("/register.html")
    return render_template("/index.html")


@app.route("/logout.html")
def logout():
    session.pop("user_id", None)
    return redirect("/index.html")
