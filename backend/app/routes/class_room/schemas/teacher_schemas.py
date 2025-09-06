from app.extensions import db
from sqlalchemy.orm import validates
import re

class Teachers(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    class_room = db.Column(db.String, default = 'update later')
    status = db.Column(db.Boolean, default = True)
    info_teacher = db.relationship('Info_teacher', back_populates = 'teachers', lazy = True)
    @validates('name')
    def name_validates(self, key, value):
        if not re.fullmatch(r'[a_zA-ZÀ-ỹ\s]+', value):
            raise ValueError('Tên không được chứa số và ký tự đặc biệt')
        return value

class Infos_teacher(db.Model):
    __tablename__ = 'infos_teacher'
    id = db.Column(db.Integer, primary_key = True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete = 'CASCADE'))
    email = db.Column(db.String, default = 'update later')
    tel = db.Column(db.String(10))
    add = db.Column(db.String, default = 'update later')
    teachers = db.relationship('Teachers', back_populates = 'info_teacher', lazy = True)
    @validates('tel')
    def tel_validates(self, key, value):
        if not re.fullmatch(r'\d{10}', value):
            return ValueError('Số điện thoại chỉ được chứa 10 chữ số!')
        return value
    
    @validates('add')
    def add_validates(self, key, value):
        if re.search('[!@#$%^&*(_+=,.<>?)]', value):
            raise ValueError('Địa chỉ không được chứa ký tự đặc biệt!')
        return value
    
    @validates('email')
    def email_validates(self, key, value):
        if re.search('[!#$%^&*-+=(),;:]', value):
            return ValueError('Email không hợp lệ!!')
        return value
