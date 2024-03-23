from flask import g
from sqlalchemy.orm import column_property, synonym

from Faab.extensions import db


class Users(db.Model):
    __bind_key__ = 'test'
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True)
    name = db.Column(db.String(255), default='')
    password = db.Column(db.String(255))
    avatar = db.Column(db.Text(1000), default='')
    is_delete = db.Column(db.Integer, default=0)


    def __repr__(self):
        return '<users %r>' % self.username
