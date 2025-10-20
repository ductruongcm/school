from app.extensions import db
from sqlalchemy.orm import validates
import re

class Teachers(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key = True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete = 'CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete = 'CASCADE'))
    name = db.Column(db.String, nullable = False)
    status = db.Column(db.Boolean, default = True)
    teacher_info = db.relationship('Teacher_info', back_populates = 'teacher', lazy = True, uselist = False)
    users = db.relationship('Users', back_populates = 'teachers', lazy = True)
    lesson = db.relationship('Lesson', back_populates = 'teachers', lazy = True)
    class_room = db.relationship('Class_room', back_populates = 'teachers', lazy = True)
    teach_class = db.relationship('Teach_class', back_populates = 'teachers', lazy = True)
    @validates('name')
    def name_validates(self, key, value):
        if not re.fullmatch(r'[a-zA-ZÀ-ỹ\s]+', value):
            raise ValueError('Tên không được chứa số và ký tự đặc biệt!!')
        return value

class Teacher_info(db.Model):
    __tablename__ = 'teacher_info'
    id = db.Column(db.Integer, primary_key = True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete = 'CASCADE'))
    email = db.Column(db.String, default = 'update later')
    tel = db.Column(db.String(10))
    add = db.Column(db.String, default = 'update later')
    teacher = db.relationship('Teachers', back_populates = 'teacher_info', lazy = True)
    @validates('tel')
    def tel_validates(self, key, value):
        if not re.fullmatch(r'\d{10}', value):
            return ValueError('Số điện thoại chỉ được chứa 10 chữ số!')
        return value
    
    @validates('add')
    def add_validates(self, key, value):
        if re.search(r"[~!@#$%^&*()_+=`,.<>/?-]+", value):
            raise ValueError('Địa chỉ không được chứa ký tự đặc biệt!')
        return value
    
    @validates('email')
    def email_validates(self, key, value):
        if re.search('[!#$%^&*-+=(),;:]', value):
            return ValueError('Email không hợp lệ!!')
        return value


