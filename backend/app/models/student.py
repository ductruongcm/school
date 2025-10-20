from app.extensions import db
from sqlalchemy.orm import validates
import re

class Students(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete = 'CASCADE'))
    name = db.Column(db.String, nullable = False)
    student_code = db.Column(db.String, unique = True)
    status = db.Column(db.Boolean, default = True)
    users = db.relationship('Users', back_populates = 'students', lazy = True)
    student_class = db.relationship('Student_Class', back_populates = 'students', lazy = True)
    rank = db.relationship('Rank', back_populates = 'students', lazy = True)
    student_info = db.relationship('Student_info', back_populates = 'students', lazy = True)
    student_lesson_period = db.relationship('Student_Lesson_Period', back_populates = 'students', lazy = True)

    @validates('name')
    def name_validates(self, key, value):
        if not re.fullmatch(r'[a-zA-ZÀ-ỹ\s]+', value):
            raise ValueError('Tên không được chứa số và ký tự đặc biệt!!')
        return value
    
    @validates('tel')
    def tel_validates(self, key, value):
        if not re.fullmatch(r'\d{10}', value):
            raise ValueError('Số điện thoại chỉ được chứa 10 số!!')
        return value
    
    @validates('add')
    def add_validates(self, key, value):
        if re.search('[!@#$%^&*(_+=,.<>?)]', value):
            raise ValueError('Địa chỉ không được chứa ký tự đặc biệt!')
        return value

class Student_info(db.Model):
    __tablename__ = 'student_info'
    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete = 'CASCADE'))
    tel = db.Column(db.String, default = 'Update later')
    add = db.Column(db.String, default = 'Update later')
    gender = db.Column(db.String, nullable = False)
    BOD = db.Column(db.Date)
    students = db.relationship('Students', back_populates = 'student_info', lazy = True)

    @validates('name')
    def name_validates(self, key, value):
        if not re.fullmatch(r'[A-Za-zÀ-ỹ\s]+', value):                      #đã cho phép gõ được tiếng việt
            raise ValueError('Tên chỉ được chứa chữ cái và khoảng trắng!')
        return value
    
    @validates('tel')
    def tel_validates(self, key, value):
        if value == '':
            return None
        elif not re.fullmatch(r'\d{10}', value):
            raise ValueError('Số điện thoại chỉ được chứa 10 số!')
        return value

class Student_Class(db.Model):
    __tablename__ = 'student_class'
    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete = 'CASCADE'))
    class_room_id = db.Column(db.Integer, db.ForeignKey('class_room.id', ondelete = 'CASCADE'))
    grade_id = db.Column(db.Integer, db.ForeignKey('grade.id', ondelete = 'CASCADE'))
    year_id = db.Column(db.Integer, db.ForeignKey('year.id', ondelete = 'CASCADE'))
    students = db.relationship('Students', back_populates = 'student_class', lazy = True)
    class_room = db.relationship('Class_room', back_populates = 'student_class', lazy = True)

class Rank(db.Model):
    __tablename__ = 'rank'
    id = db.Column(db.Integer, primary_key = True)
    students_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete = 'CASCADE'))
    rank = db.Column(db.String(10))
    students = db.relationship('Students', back_populates = 'rank', lazy = True)    

class Score(db.Model):
    __tablename__ = 'score'
    id = db.Column(db.Integer, db.ForeignKey('student_lesson_period.id', ondelete = 'CASCADE'), primary_key = True)
    score_oral = db.Column(db.Float)
    score_15m = db.Column(db.Float)
    score_45m = db.Column(db.Float)
    score_final = db.Column(db.Float)
    total = db.Column(db.Float)
    remark = db.Column(db.String)
    student_lesson_period = db.relationship('Student_Lesson_Period', back_populates = 'score', lazy = True)

    @validates('score_oral', 'score_15m', 'score_45m',
               'score_final', 'total')
    def score_validates(self, key, value):
        if value < 0 or value > 10:
            raise ValueError('điểm số không được âm với lớn hơn 10!!')
        if not re.fullmatch(r'\d.', value):
            raise ValueError('Chỉ được chứa số!!')
        return value
    

