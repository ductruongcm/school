from app.extensions import db
from datetime import datetime

class Class_room(db.Model):
    __tablename__ = 'class_room'
    id = db.Column(db.Integer, primary_key = True)
    year_id = db.Column(db.Integer, db.ForeignKey('year.id', ondelete = 'CASCADE'))
    grade_id = db.Column(db.Integer, db.ForeignKey('grade.id', ondelete = 'CASCADE'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete = 'CASCADE'))
    class_room = db.Column(db.String, unique = True, nullable = False)
    status = db.Column(db.Boolean, default = True)
    year = db.relationship('Year', back_populates = 'class_room', lazy = True)
    student_class = db.relationship('Student_Class', back_populates = 'class_room', lazy = True)
    teachers = db.relationship('Teachers', back_populates = 'class_room', lazy = True)
    teach_class = db.relationship('Teach_class', back_populates = 'class_room', lazy = True)
    grade = db.relationship('Grade', back_populates = 'class_room', lazy = True)
    
class Schedule(db.Model):
    __tablename__ = 'schedule'
    id = db.Column(db.Integer, primary_key = True)
    class_room_id = db.Column(db.Integer, db.ForeignKey('class_room.id', ondelete = 'CASCADE'))
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id', ondelete = 'CASCADE'))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete = 'CASCADE'))
    weekday = db.Column(db.Integer)
    period = db.Column(db.Integer)

class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete = 'CASCADE'))
    title = db.Column(db.String)
    message = db.Column(db.Text)
    type = db.Column(db.String)
    is_read = db.Column(db.Boolean, default = False)
    created_at = db.Column(db.DateTime, default = datetime.utcnow)

class Semester(db.Model):
    __tablename__ = 'semester'
    id = db.Column(db.Integer, primary_key = True)   
    semester = db.Column(db.String(5), nullable = False)

class Period(db.Model):
    __tablename__ = 'period'
    id = db.Column(db.Integer, primary_key = True)   
    year_id = db.Column(db.Integer, db.ForeignKey('year.id', ondelete = 'CASCADE'), nullable = False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id', ondelete = 'CASCADE'), nullable = False)
    student_lesson_period = db.relationship('Student_Lesson_Period', back_populates = 'period', lazy = True)

class Teach_class(db.Model):
    __tablename__ = 'teach_class'
    id = db.Column(db.Integer, primary_key = True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete = 'CASCADE'))
    class_room_id = db.Column(db.Integer, db.ForeignKey('class_room.id', ondelete = 'CASCADE'), nullable = False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete = 'CASCADE'), nullable = False)
    year_id = db.Column(db.Integer, db.ForeignKey('year.id', ondelete = 'CASCADE'), nullable = False)
    teachers = db.relationship('Teachers', back_populates = 'teach_class', lazy = True)   
    class_room = db.relationship('Class_room', back_populates = 'teach_class', lazy = True)
    lesson = db.relationship('Lesson', back_populates = 'teach_class', lazy = True)
    files = db.relationship('Files', back_populates = 'teach_class', lazy = True)

class Student_Lesson_Period(db.Model):
    __tablename__ = 'student_lesson_period'
    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete = 'CASCADE'))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete = 'CASCADE'))
    period_id = db.Column(db.Integer, db.ForeignKey('period.id', ondelete = 'CASCADE'))
    student_status = db.Column(db.Boolean, default = True)
    students = db.relationship('Students', back_populates = 'student_lesson_period', lazy = True)
    lesson = db.relationship('Lesson', back_populates = 'student_lesson_period', lazy = True)
    period = db.relationship('Period', back_populates = 'student_lesson_period', lazy = True)
    score = db.relationship('Score', back_populates = 'student_lesson_period', lazy = True)

class Lesson(db.Model):
    __tablename__ = 'lesson'
    id = db.Column(db.Integer, primary_key = True)
    year_id = db.Column(db.Integer, db.ForeignKey('year.id', ondelete = 'CASCADE'), nullable = False)
    grade_id = db.Column(db.Integer, db.ForeignKey('grade.id', ondelete = 'CASCADE'), nullable = False)
    lesson = db.Column(db.String(15), nullable = False)
    grade = db.relationship('Grade', back_populates = 'lesson', lazy = True)
    teachers = db.relationship('Teachers', back_populates = 'lesson', lazy = True)    
    teach_class = db.relationship('Teach_class', back_populates = 'lesson', lazy = True)
    student_lesson_period = db.relationship('Student_Lesson_Period', back_populates = 'lesson', lazy = True)

class Grade(db.Model):
    __tablename__ = 'grade'
    id = db.Column(db.Integer, primary_key = True)
    grade = db.Column(db.Integer, nullable = True)
    grade_status = db.Column(db.Boolean, default = True)
    class_room = db.relationship('Class_room', back_populates = 'grade', lazy = True)
    lesson = db.relationship('Lesson', back_populates = 'grade', lazy = True)

class Year(db.Model):
    __tablename__ = 'year'
    id = db.Column(db.Integer, primary_key = True)
    year = db.Column(db.String, unique = True, nullable = False)
    is_active = db.Column(db.Boolean, default = False)
    class_room = db.relationship('Class_room', back_populates = 'year', lazy = True)

