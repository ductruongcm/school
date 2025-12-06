from app.extensions import db
from sqlalchemy.orm import validates
from sqlalchemy import UniqueConstraint
from datetime import datetime
import re

class Students(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete = 'CASCADE'))
    name = db.Column(db.String, nullable = False)
    student_code = db.Column(db.String, unique = True)
    status = db.Column(db.Boolean, default = True)
    users = db.relationship('Users', back_populates = 'students', lazy = True)
    student_info = db.relationship('Student_info', back_populates = 'students', lazy = True)
    student_lesson_period = db.relationship('Student_Lesson_Period', back_populates = 'students', lazy = True)
    student_lesson_annual = db.relationship('Student_Lesson_Annual', back_populates = 'students', lazy = True)
    student_year_summary = db.relationship('Student_Year_Summary', back_populates = 'students', lazy = True)
    student_period_summary = db.relationship('Student_Period_Summary', back_populates = 'students', lazy = True)
    attendence = db.relationship('Attendence', back_populates = 'students', lazy = True)

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
    note = db.Column(db.String(100))
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
    
class Student_Lesson_Period(db.Model):
    __tablename__ = 'student_lesson_period'
    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete = 'CASCADE'))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete = 'SET NULL'))
    period_id = db.Column(db.Integer, db.ForeignKey('period.id', ondelete = 'CASCADE'))
    total = db.Column(db.Float)
    status = db.Column(db.String(15))
    note = db.Column(db.Text)
    students = db.relationship('Students', back_populates = 'student_lesson_period', lazy = True)
    lesson = db.relationship('Lesson', back_populates = 'student_lesson_period', lazy = True)
    period = db.relationship('Period', back_populates = 'student_lesson_period', lazy = True)
    score = db.relationship('Score', back_populates = 'student_lesson_period', lazy = True)
    __table_args__ = (UniqueConstraint('student_id', 'period_id', 'lesson_id', name='stu_ls_per_uniq'),)

class Student_Lesson_Annual(db.Model):
    __tablename__ = 'student_lesson_annual'
    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete = 'SET NULL'))
    year_id = db.Column(db.Integer, db.ForeignKey('year.id', ondelete = 'CASCADE'))
    avg_annual = db.Column(db.Float)
    status = db.Column(db.String(15))
    students = db.relationship('Students', back_populates = 'student_lesson_annual', lazy = True)
    lesson = db.relationship('Lesson', back_populates = 'student_lesson_annual', lazy = True)
    __table_args__ = (UniqueConstraint('student_id', 'lesson_id', 'year_id', name = 'stu_ls_year_uniq'),)

class Student_Period_Summary(db.Model):
    __tablename__ = 'student_period_summary'
    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete = 'CASCADE'), nullable = False)
    period_id = db.Column(db.Integer, db.ForeignKey('period.id', ondelete = 'CASCADE'), nullable = False)
    class_room_id = db.Column(db.Integer, db.ForeignKey('class_room.id', ondelete = 'NO ACTION'))
    grade = db.Column(db.Integer, db.ForeignKey('grade.grade', ondelete = 'NO ACTION'), nullable = False)
    score = db.Column(db.Float)
    conduct = db.Column(db.String(15))
    absent_day = db.Column(db.Integer, default = 0)
    status = db.Column(db.String(20))
    note = db.Column(db.String(100))
    students = db.relationship('Students', back_populates = 'student_period_summary', lazy = True)
    __table_agrs__ = (UniqueConstraint('student_id', 'period_id', name = 'stu_per_uniq'),)

class Student_Year_Summary(db.Model):
    __tablename__ = 'student_year_summary'
    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete = 'CASCADE'))
    year_id = db.Column(db.Integer, db.ForeignKey('year.id', ondelete = 'CASCADE'))
    class_room_id = db.Column(db.Integer, db.ForeignKey('class_room.id', ondelete = 'SET NULL'))
    grade = db.Column(db.Integer, db.ForeignKey('grade.grade', ondelete = 'NO ACTION'))
    score = db.Column(db.Float)
    conduct = db.Column(db.String(15))
    learning_status = db.Column(db.String(15))
    absent_day = db.Column(db.Integer, default = 0)
    status = db.Column(db.String(20))
    review_status = db.Column(db.Boolean, default = False)
    assign_status = db.Column(db.Boolean, default = False)
    note = db.Column(db.String(100))
    transfer_info = db.Column(db.String(100))
    students = db.relationship('Students', back_populates = 'student_year_summary', lazy = True)
    __table_args__ = (UniqueConstraint('student_id', 'year_id', name='stu_year_uniq'),)

class Attendence(db.Model):
    __tablename__ = 'attendence'
    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete = 'CASCADE'), nullable = False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id', ondelete = 'CASCADE'), nullable = False)
    status = db.Column(db.String(1), default = 'P')
    datetime = db.Column(db.DateTime, default = datetime.utcnow)
    students = db.relationship('Students', back_populates = 'attendence', lazy = True)
    schedule = db.relationship('Schedule', back_populates = 'attendence', lazy = True)
    attendence_note = db.relationship('Attendence_Note', back_populates = 'attendence', lazy = True)
    __table_args__ = (UniqueConstraint('student_id', 'schedule_id', name='stu_sch_uniq'),)

    @validates('status')
    def validate_status(self, key, value):
        if value not in ['P', 'A', 'E']:
            raise ValueError('Thông tin input không chính xác!')
        
        return value
    
class Attendence_Note(db.Model):
    __table_name__ = 'attendence_note'
    id = db.Column(db.Integer, primary_key = True)
    attendence_id = db.Column(db.Integer, db.ForeignKey('attendence.id', ondelete = 'CASCADE'), nullable = False)
    note = db.Column(db.String(100))
    attendence = db.relationship('Attendence', back_populates = 'attendence_note', lazy = True)