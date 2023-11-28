from flask_sqlalchemy import SQLAlchemy
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    publickey = db.Column(db.String(100000), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.id}')"


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.Integer, nullable=False)
    reciever = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String)
    time = db.Column(db.String, nullable=False)


class Keys(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(1000), nullable=False)
    privateKey = db.Column(db.String(100000), nullable=False)


