from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    birthdate = db.Column(db.Date)
    password_hash = db.Column(db.String(128))
    marks = db.Column(db.Integer, index=True)

    # def __init__(self):

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Questions(db.Model):
    q_id = db.Column(db.Integer, primary_key=True)
    ques = db.Column(db.String(350), unique=True)
    a = db.Column(db.String(100))
    b = db.Column(db.String(100))
    c = db.Column(db.String(100))
    d = db.Column(db.String(100))
    e = db.Column(db.String(100))
    f = db.Column(db.String(100))
    g = db.Column(db.String(100))
    instr = db.Column(db.String(500))


class Sessions(db.Model):
    s_id = db.Column(db.Integer, primary_key=True)
    s_uid = db.Column(db.String(50))
    u_id = db.Column(db.Integer, ForeignKey(User.id))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    user = relationship('User', foreign_keys='Sessions.u_id')

    # def __init__(self):

    def __repr__(self):
        return '<Question: {}>'.format(self.ques)


class Results(db.Model):
    r_id = db.Column(db.Integer, primary_key=True)
    u_id = db.Column(db.Integer, ForeignKey(User.id))
    s_uid = db.Column(db.String(50), ForeignKey(Sessions.s_uid))
    q_id = db.Column(db.Integer, ForeignKey(Questions.q_id))
    answ = db.Column(db.String(100))
    q_requested_timestamp = db.Column(db.DateTime)
    timestamp = db.Column(db.DateTime)

    user = relationship('User', foreign_keys='Results.u_id')
    session = relationship('Sessions', foreign_keys='Results.s_uid')
    question = relationship('Questions', foreign_keys='Results.q_id', lazy='joined')
    # def __init__(self):

    def __repr__(self):
        return '<Result of user {}>'.format(self.u_id)