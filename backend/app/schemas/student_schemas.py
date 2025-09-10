from app.extensions import db
from sqlalchemy.orm import validates
# from app.schemas import Class_room
import re

class Students(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key = True)
    class_room_id = db.Column(db.Integer, db.ForeignKey('class_room.id', ondelete = 'CASCADE'))
    info_id = db.Column(db.Integer, db.ForeignKey('info.id', ondelete = 'CASCADE'))
    name = db.Column(db.String, nullable = False)
    status = db.Column(db.Boolean, default = True)
    student_id = db.Column(db.Integer)
    class_room = db.relationship('Class_room', back_populates = 'students', lazy = True)
    mark = db.relationship('Mark', back_populates = 'students', lazy = True)
    rank = db.relationship('Rank', back_populates = 'students', lazy = True)
    info = db.relationship('Info', back_populates = 'students', lazy = True)
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
    
class Mark(db.Model):
    __tablename__ = 'mark'
    id = db.Column(db.Integer, primary_key = True)
    students_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete = 'CASCADE'))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete = 'CASCADE'))
    mark_1_15_1 = db.Column(db.Float, default = 0)
    mark_1_15_2 = db.Column(db.Float, default = 0)
    mark_1_45 = db.Column(db.Float, default = 0)
    mark_1_15_3 = db.Column(db.Float, default = 0)
    mark_1_15_4 = db.Column(db.Float, default = 0)
    mark_1 = db.Column(db.Float, default = 0)
    mark_2_15_1 = db.Column(db.Float, default = 0)
    mark_2_15_2 = db.Column(db.Float, default = 0)
    mark_2_45 = db.Column(db.Float, default = 0)
    mark_2_15_3 = db.Column(db.Float, default = 0)
    mark_2_15_4 = db.Column(db.Float, default = 0)
    mark_2 = db.Column(db.Float, default = 0)
    final = db.Column(db.Float, default = 0)
    students = db.relationship('Students', back_populates = 'mark', lazy = True)
    rank = db.relationship('Rank', back_populates = 'mark', lazy = True)
    lesson = db.relationship('Lesson', back_populates = 'mark', lazy = True)
    @validates(
        'mark_1_15_1', 'mark_1_15_2', 'mark_1_45',
        'mark_1_15_3', 'mark_1_15_4', 'mark_1'
        'mark_2_15_1', 'mark_2_15_2', 'mark_2_45',
        'mark_2_15_3', 'mark_2_15_4', 'mark_2', 'final'
    )
    def mark_validates(self, key, value):
        if value < 0:
            raise ValueError('Điểm không có âm!')
        elif value > 10:
            raise ValueError('Điểm 10 là maximum rồi!')
        return value
    
class Rank(db.Model):
    __tablename__ = 'rank'
    id = db.Column(db.Integer, primary_key = True)
    students_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete = 'CASCADE'))
    mark_id = db.Column(db.Integer, db.ForeignKey('mark.id', ondelete = 'CASCADE'))
    average_1_1 = db.Column(db.Float, default = 0) 
    average_1_2 = db.Column(db.Float, default = 0) 
    average_2_1 = db.Column(db.Float, default = 0) 
    average_2_2 = db.Column(db.Float, default = 0)
    rank = db.Column(db.String(10))
    students = db.relationship('Students', back_populates = 'rank', lazy = True)
    mark = db.relationship('Mark', back_populates = 'rank', lazy = True)

            

