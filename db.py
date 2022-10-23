from os import getenv
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import sqlalchemy as sa
from flask_sqlalchemy import SQLAlchemy
from flask import session, flash

db = SQLAlchemy()
ph = PasswordHasher()

# TODO sanity checking for the lengths when sending form
#   - max lengths are 30 for shor fields and 10k for long fields
# TODO create schema.sql (see https://hy-tsoha.github.io/materiaali/osa-3/)


class Users(db.Model):
    user_id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(30), unique=True, nullable=False)
    pw_hash = sa.Column(sa.String, unique=True, nullable=False)


class Tasks(db.Model):
    task_id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.user_id"), nullable=False)
    content = sa.Column(sa.String(10000), nullable=False)
    due_date = sa.Column(sa.Date, nullable=False)


class Notes(db.Model):
    note_id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.user_id"), nullable=False)
    content = sa.Column(sa.String(10000), nullable=False)


class Tags(db.Model):
    tag_id = sa.Column(sa.Integer, primary_key=True)
    tag_name = sa.Column(sa.String(30), nullable=False)


class NoteTag(db.Model):
    notetag_id = sa.Column(sa.Integer, primary_key=True)
    note_id = sa.Column(sa.Integer, sa.ForeignKey("notes.note_id"), nullable=False)
    tag_id = sa.Column(sa.Integer, sa.ForeignKey("tags.tag_id"), nullable=False)


class Db():
    def __init__(self, app):
        # Load environment variable from local .env file in the project
        db_url = getenv("DATABASE_URL")

        # Heroku-specific hack so the database connection works
        # The protocol heroku sets is "postgres://" when it should be
        # "postgresql://" This hack rewrites it. Unfortunately this also means
        # the file in .env needs to take this into account.
        SQLALCHEMY_DATABASE_URI = db_url.replace("://", "ql://", 1)

        app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
        db.init_app(app)
        with app.app_context():
            db.create_all()

    def try_register(self, username, password):
        if len(username) == 0 or len(password) == 0:
            flash("Username or password must not be empty.", category="error")
            return False
        if len(password) > 1000:
            flash("Password must not be longer than 1000 characters.", category="error");
            return False
        if len(username) > 30:
            flash("Username must not be longer than 30 characters.", category="error");
            return False

        sql = "SELECT username FROM users WHERE LOWER(users.username) = LOWER(:username) LIMIT 1"
        result = db.session.execute(sql, {"username": username})
        messages = result.fetchone()
        # User doesn't exist, create account
        if not messages:
            # The argon2 hasher stores the salt internally and it doesn't need
            # separate storing in the database.
            pw_hash = ph.hash(password)

            sql = "INSERT INTO users (username, pw_hash) \
                    VALUES (:username, :pw_hash)"
            db.session.execute(sql, {"username": username, "pw_hash": pw_hash})
            db.session.commit()
            return True
        # User exists already
        flash("Username is not available.", category="error");
        return False

    def try_login(self, username, password):
        sql = "SELECT pw_hash FROM users WHERE users.username = :username LIMIT 1"
        result = db.session.execute(sql, {"username": username})
        pw_hash = result.fetchone()
        if pw_hash:
            try:
                ph.verify(pw_hash[0], password)
                return True
            except VerifyMismatchError:
                return False
        else:
            return False

    def user_id_for(self, username):
        sql = "SELECT user_id FROM users WHERE users.username = :username LIMIT 1"
        result = db.session.execute(sql, {"username": username})
        messages = result.fetchone()
        return messages[0]

    def post_note(self, content):
        sql = "INSERT INTO notes (content, user_id) VALUES (:content, :user_id)"
        db.session.execute(sql, {"content": content, "user_id": session["user_id"]})
        db.session.commit()

    def delete_note(self, note_id):
        sql = "DELETE FROM notes WHERE user_id = (:user_id) AND note_id = (:note_id)"
        db.session.execute(sql, {"user_id": session["user_id"], "note_id": note_id})
        db.session.commit()

    def get_notes(self):
        sql = "SELECT content, note_id FROM notes WHERE (user_id) = :user_id"
        return db.session.execute(sql, {"user_id": session["user_id"]}).fetchall()

    def post_task(self, content, due_date):
        sql = "INSERT INTO tasks (content, user_id, due_date) VALUES (:content, :user_id, :due_date)"
        db.session.execute(sql, {"content": content, "due_date": due_date, "user_id": session["user_id"]})
        db.session.commit()

    def delete_task(self, task_id):
        sql = "DELETE FROM tasks WHERE user_id = (:user_id) AND task_id = (:task_id)"
        db.session.execute(sql, {"user_id": session["user_id"], "task_id": task_id})
        db.session.commit()

    def get_tasks(self):
        sql = "SELECT content, task_id, due_date FROM tasks WHERE (user_id) = :user_id ORDER BY due_date"
        return db.session.execute(sql, {"user_id": session["user_id"]}).fetchall()
