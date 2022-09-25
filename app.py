from flask import Flask, flash, session, redirect, render_template, request
from db import Db

app = Flask(__name__)
# temporary value, this isn't used yet
app.secret_key = "hunter2"
db = Db(app)


@app.route("/")
def root():
    return redirect("index.html")


@app.route("/index.html")
def index():
    return render_template("index.html")


@app.route("/login.html", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["username"] = request.form["username"]
        return redirect("/")
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


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/index.html")


# @app.route("/send", methods=["POST"])
# def send():
#     content = request.form["content"]
#     sql = "INSERT INTO messages (content) VALUES (:content)"
#     db.session.execute(sql, {"content": content})
#     db.session.commit()
#     return redirect("/")
