from app.extensions import db
from sqlalchemy.orm import validates
from datetime import datetime, timedelta
import re

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique = True, nullable = False)
    password = db.Column(db.String, nullable = False)
    role = db.Column(db.String, default = 'guest')
    status = db.Column(db.Boolean, default = True)
    is_finalize = db.Column(db.Boolean, default = False)
    students = db.relationship('Students', back_populates = 'users', lazy = True)
    teachers = db.relationship('Teachers', back_populates = 'users', lazy = True)
    cloud = db.relationship('Cloud', back_populates = 'users', lazy = True)
    tmp_token = db.relationship('Tmp_token', back_populates = 'users', lazy = True)

    @validates('username')
    def username_validates(self, key, value):
        if not re.fullmatch(r'[a-z0-9_]{8,}', value):
            raise ValueError('Username phải có ít nhất 8 ký tự, và chỉ được chứa chữ cái thường và số')
        return value

    @validates('password')
    def password_validates(self, key, value):
        if not re.fullmatch(r'(?=.*\d)(?=.*[!@#$%^&*])(?=.*[A-Z]).{8,}', value):
            raise ValueError('Password phải có ít nhất 8 ký tự và chứa ít nhất 1 ký tự đặc biệt, 1 số và 1 chữ in hoa')
        return value

class Tmp_token(db.Model):
    __tablename__ = 'tmp_token'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete = 'CASCADE'))    
    token = db.Column(db.String)
    expire_at = db.Column(db.DateTime, default = lambda: datetime.utcnow() + timedelta(hours=7))
    set_password_status = db.Column(db.Boolean, default = False)
    users = db.relationship('Users', back_populates = 'tmp_token', lazy = True)
