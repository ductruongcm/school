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
    students = db.relationship('Students', back_populates = 'class_room', lazy = True)
    teachers = db.relationship('Teachers', back_populates = 'class_room', lazy = True)
    teach_room = db.relationship('Teach_room', back_populates = 'class_room', lazy = True)
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
    year_id = db.Column(db.Integer, db.ForeignKey('year.id', ondelete = 'CASCADE'))

class Class_lesson(db.Model):
    __tablename__ = 'class_lesson'
    id = db.Column(db.Integer, primary_key = True)
    grade_id = db.Column(db.Integer, db.ForeignKey('class_room.id', ondelete = 'CASCADE'))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete = 'CASCADE'))

class Grade(db.Model):
    __tablename__ = 'grade'
    id = db.Column(db.Integer, primary_key = True)
    grade = db.Column(db.Integer, nullable = True)
    grade_status = db.Column(db.Boolean, default = True)
    class_room = db.relationship('Class_room', back_populates = 'grade', lazy = True)

class Year(db.Model):
    __tablename__ = 'year'
    id = db.Column(db.Integer, primary_key = True)
    year = db.Column(db.String, unique = True, nullable = False)
    class_room = db.relationship('Class_room', back_populates = 'year', lazy = True)