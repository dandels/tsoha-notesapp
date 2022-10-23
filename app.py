from os import getenv
from flask import Flask, flash, session, redirect, render_template, request, abort
from db import Db
from dotenv import load_dotenv
import secrets

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
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        if "new-note" in request.form:
            db.post_note(request.form["new-note"])
        elif "delete-note" in request.form:
            db.delete_note(request.form["note-id"])
        else:
            abort(400)

    session["csrf_token"] = secrets.token_hex(16)
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
            flash("Invalid username or password.", category="error")
    return render_template("login.html")


@app.route("/register.html", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        session["csrf_token"] = secrets.token_hex(16)
        return render_template("/register.html")
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        elif db.try_register(request.form["username"], request.form["password"]):
            flash("Username not available.", category="error")
            session["user_id"] = db.user_id_for(request.form["username"])
            return redirect("/index.html")
        else:
            flash("Username not available.", category="error")
            return render_template("/register.html")


@app.route("/logout.html")
def logout():
    session.pop("user_id", None)
    return redirect("/index.html")
