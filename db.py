from os import getenv
from dotenv import load_dotenv
from argon2 import PasswordHasher
import sqlalchemy as sa
from sqlalchemy import Table, Column, Integer, String, MetaData, DateTime,\
        ForeignKey
from flask_sqlalchemy import SQLAlchemy

# metadata = MetaData()
db = SQLAlchemy()

# Table(
#     "users", metadata,
#     Column("user_id", Integer, primary_key=True),
#     Column("username", String),
#     Column("pw_hash", String),
#     )
#
# Table(
#     "notes", metadata,
#     Column("note_id", Integer, primary_key=True),
#     Column("user_id", Integer, ForeignKey("users.user_id")),
#     Column("content", String),
#     )
#
# Table(
#     "todo", metadata,
#     Column("todo_id", Integer, primary_key=True),
#     Column("user_id", Integer, ForeignKey("users.user_id")),
#     Column("content", String),
#     Column("date", DateTime),
#     )


class Users(db.Model):
    user_id = sa.Column(Integer, primary_key=True)
    username = sa.Column(sa.String, unique=True, nullable=False)
    pw_hash = sa.Column(sa.String, unique=True, nullable=False)


class Db():
    def __init__(self, app):
        load_dotenv()
        app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
        db.init_app(app)
        with app.app_context():
            db.create_all()

    def hash_pw(self, name, password):
        # The argon2 hasher stores the salt internally and it doesn't need
        # separate storing in the database.
        hasher = PasswordHasher()
        pw_hash = hasher.hash(password)
        return pw_hash

    def try_register(self, name, password):
        sql = "SELECT 1 FROM users WHERE users.username = :name"
        result = db.session.execute(sql, {"name": name})
        messages = result.fetchall()
        print("messages", messages)
        # User doesn't exist, create account
        if not messages:
            pw_hash = self.hash_pw(name, password)
            sql = "INSERT INTO users (username, pw_hash) \
                    VALUES (:name, :pw_hash)"
            db.session.execute(sql, {"name": name, "pw_hash": pw_hash})
            db.session.commit()
            print(name, " ", pw_hash)
            return True
        # User exists already
        return False

    def authenticate(self, name, password):
        return None
