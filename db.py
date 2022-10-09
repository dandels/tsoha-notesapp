from os import getenv
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import sqlalchemy as sa
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Users(db.Model):
    user_id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String, unique=True, nullable=False)
    pw_hash = sa.Column(sa.String, unique=True, nullable=False)


class Todo(db.Model):
    todo_id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.user_id"), nullable=False)
    content = sa.Column(sa.String)
    due_date = sa.Column(sa.DateTime)


class Notes(db.Model):
    note_id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.user_id"), nullable=False)
    content = sa.Column(sa.String)


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

    def try_register(self, name, password):
        sql = "SELECT username FROM users WHERE users.username = :name LIMIT 1"
        result = db.session.execute(sql, {"name": name})
        messages = result.fetchone()
        # User doesn't exist, create account
        if not messages:
            # The argon2 hasher stores the salt internally and it doesn't need
            # separate storing in the database.
            pw_hash = PasswordHasher.hash(password)

            sql = "INSERT INTO users (username, pw_hash) \
                    VALUES (:name, :pw_hash)"
            db.session.execute(sql, {"name": name, "pw_hash": pw_hash})
            db.session.commit()
            print(name, " ", pw_hash)
            return True
        # User exists already
        return False

    def try_login(self, name, password):
        sql = "SELECT pw_hash FROM users WHERE users.username = :name LIMIT 1"
        result = db.session.execute(sql, {"name": name})
        pw_hash = result.fetchone()
        if pw_hash:
            try:
                ph = PasswordHasher()
                ph.verify(pw_hash[0], password)
                return True
            except VerifyMismatchError:
                return False
        else:
            return False
