from app.extensions import db
from sqlalchemy.orm import validates
import re

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique = True, nullable = False)
    password = db.Column(db.String, nullable = False)
    email = db.Column(db.String, unique = True, nullable = False)
    role = db.Column(db.String, default = 'guest')
    status = db.Column(db.Boolean, default = True)
    is_finalize = db.Column(db.Boolean, default = False)
    info = db.relationship('Info', back_populates = 'users', lazy = True)
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
    
class Info(db.Model):
    __tablename__ = 'info'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete = 'CASCADE'))
    name = db.Column(db.String, nullable = False)
    tel = db.Column(db.String, default = 'Update later')
    add = db.Column(db.String, default = 'Update later')
    class_room = db.Column(db.String, default = 'Update later')
    users = db.relationship('Users', back_populates = 'info', lazy = True)

    @validates('name')
    def name_validates(self, key, value):
        if not re.fullmatch(r'[A-Za-zÀ-ỹ\s]+', value):                      #đã cho phép gõ được tiếng việt
            raise ValueError('Tên chỉ được chứa chữ cái và khoảng trắng!')
        return value
    
    @validates('tel')
    def tel_validates(self, key, value):
        if not re.fullmatch(r'\d{10}', value):
            raise ValueError('Số điện thoại chỉ được chứa 10 số!')
        return value