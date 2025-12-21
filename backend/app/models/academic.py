from app.extensions import db
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import validates
from datetime import date

class Class_room(db.Model):
    __tablename__ = 'class_room'
    id = db.Column(db.Integer, primary_key = True)
    year_id = db.Column(db.Integer, db.ForeignKey('year.id', ondelete = 'CASCADE'))
    grade = db.Column(db.Integer, db.ForeignKey('grade.grade', ondelete = 'CASCADE'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete = 'SET NULL'))
    class_room = db.Column(db.String, nullable = False)
    status = db.Column(db.Boolean, default = True)
    year = db.relationship('Year', back_populates = 'class_room', lazy = True)
    teachers = db.relationship('Teachers', back_populates = 'class_room', lazy = True)
    teach_class = db.relationship('Teach_class', back_populates = 'class_room', lazy = True)
    grade_obj = db.relationship('Grade', back_populates = 'class_room', lazy = True)
    __table_args__ = (UniqueConstraint('year_id', 'class_room', name='year_class_uniq'), UniqueConstraint('year_id', 'teacher_id', name = 'year_teacher_uniq'))
    
class Schedule(db.Model):
    __tablename__ = 'schedule'
    id = db.Column(db.Integer, primary_key = True)
    class_room_id = db.Column(db.Integer, db.ForeignKey('class_room.id', ondelete = 'CASCADE'), nullable = False)
    period_id = db.Column(db.Integer, db.ForeignKey('period.id', ondelete = 'CASCADE'), nullable = False)
    day_of_week = db.Column(db.Integer, nullable = False)
    lesson_time = db.Column(db.Integer, nullable = False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete = 'CASCADE'), nullable = False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete = 'CASCADE'))
    lesson = db.relationship('Lesson', back_populates = 'schedule', lazy = True)
    period = db.relationship('Period', back_populates = 'schedule', lazy = True)
    teachers = db.relationship('Teachers', back_populates = 'schedule', lazy = True)
    __table_args__ = (UniqueConstraint('period_id', 'class_room_id', 'day_of_week', 'lesson_time', name='schedule_uniq'),
                      UniqueConstraint('period_id', 'day_of_week', 'lesson_time', 'teacher_id', name='schedule_teacher_uniq'))

class Semester(db.Model):
    __tablename__ = 'semester'
    id = db.Column(db.Integer, primary_key = True)   
    semester = db.Column(db.String(5), nullable = False)
    weight = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default = False)

class Period(db.Model):
    __tablename__ = 'period'
    id = db.Column(db.Integer, primary_key = True)   
    year_id = db.Column(db.Integer, db.ForeignKey('year.id', ondelete = 'CASCADE'), nullable = False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id', ondelete = 'CASCADE'), nullable = False)
    student_lesson_period = db.relationship('Student_Lesson_Period', back_populates = 'period', lazy = True)
    schedule = db.relationship('Schedule', back_populates = 'period', lazy = True)
    attendence = db.relationship('Attendence', back_populates = 'period', lazy = True)

class Teach_class(db.Model):
    __tablename__ = 'teach_class'
    id = db.Column(db.Integer, primary_key = True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete = 'SET NULL'))
    class_room_id = db.Column(db.Integer, db.ForeignKey('class_room.id', ondelete = 'CASCADE'), nullable = False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete = 'CASCADE'), nullable = False)
    year_id = db.Column(db.Integer, db.ForeignKey('year.id', ondelete = 'CASCADE'), nullable = False)
    teachers = db.relationship('Teachers', back_populates = 'teach_class', lazy = True)   
    class_room = db.relationship('Class_room', back_populates = 'teach_class', lazy = True)
    lesson = db.relationship('Lesson', back_populates = 'teach_class', lazy = True)
    files = db.relationship('Files', back_populates = 'teach_class', lazy = True)
    __table_args__ = (UniqueConstraint('class_room_id', 'lesson_id', 'year_id', name = 'uq_cls_les_year'),)

class Lesson(db.Model):
    __tablename__ = 'lesson'
    id = db.Column(db.Integer, primary_key = True)
    grade = db.Column(db.Integer, db.ForeignKey('grade.grade', ondelete = 'CASCADE'), nullable = False)
    lesson = db.Column(db.String(15), nullable = False)
    status = db.Column(db.Boolean, default = True)
    grade_obj = db.relationship('Grade', back_populates = 'lesson', lazy = True)
    teachers = db.relationship('Teachers', back_populates = 'lesson', lazy = True)    
    teach_class = db.relationship('Teach_class', back_populates = 'lesson', lazy = True)
    student_lesson_period = db.relationship('Student_Lesson_Period', back_populates = 'lesson', lazy = True)
    student_lesson_annual = db.relationship('Student_Lesson_Annual', back_populates = 'lesson', lazy = True)
    schedule = db.relationship('Schedule', back_populates = 'lesson', lazy = True)
    lessontag = db.relationship('LessonTag', back_populates = 'lesson', lazy = True)
    retest = db.relationship('Retest', back_populates = 'lesson', lazy = True)

class LessonTag(db.Model):
    __tablename__ = 'lessontag'
    id = db.Column(db.Integer, primary_key = True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete = 'CASCADE'))
    is_folder = db.Column(db.Boolean)
    is_visible = db.Column(db.Boolean,)
    is_schedule = db.Column(db.Boolean)
    lesson = db.relationship('Lesson', back_populates = 'lessontag', lazy = True)

class Grade(db.Model):
    __tablename__ = 'grade'
    id = db.Column(db.Integer, primary_key = True)
    grade = db.Column(db.Integer, unique = True, nullable = True)
    grade_status = db.Column(db.Boolean, default = True)
    class_room = db.relationship('Class_room', back_populates = 'grade_obj', lazy = True)
    lesson = db.relationship('Lesson', back_populates = 'grade_obj', lazy = True)

class Year(db.Model):
    __tablename__ = 'year'
    id = db.Column(db.Integer, primary_key = True)
    year_code = db.Column(db.String, unique = True, nullable = False)
    start_date = db.Column(db.Date, nullable = False)
    end_date = db.Column(db.Date, nullable = False)
    is_active = db.Column(db.Boolean, default = False)
    class_room = db.relationship('Class_room', back_populates = 'year', lazy = True)

class Score(db.Model):
    __tablename__ = 'score'
    id = db.Column(db.Integer, primary_key = True)
    student_lesson_period_id = db.Column(db.Integer, db.ForeignKey('student_lesson_period.id', ondelete='CASCADE'), nullable = False)
    score_type_id = db.Column(db.Integer, db.ForeignKey('score_type.id', ondelete='NO ACTION'))
    attempt = db.Column(db.Integer, nullable = False)
    score = db.Column(db.Float, nullable = False)
    created_at = db.Column(db.Date, default = date.today)
    score_type = db.relationship('Score_Type', back_populates = 'score', lazy = True)
    student_lesson_period = db.relationship('Student_Lesson_Period', back_populates = 'score', lazy = True)
    __table_args__ = (UniqueConstraint('student_lesson_period_id', 'score_type_id', 'attempt', name='score_uniq'),)

    @validates('score')
    def score_validates(self, key, value):
        if value < 0 or value > 10:
            raise ValueError('điểm số không được âm với lớn hơn 10!!')
        
        if not isinstance(value, float):
            raise ValueError('Điểm số phải là số!!')
        
        return value
    
    @validates('attempt')
    def attempt_validates(self, key, value):
        if value not in [1,2,3,4]:
            raise ValueError('Attempt không hợp lệ!')
        
        return value

class Score_Type(db.Model):
    __tablename__ = 'score_type'
    id = db.Column(db.Integer, primary_key = True)
    score_type = db.Column(db.String(15), nullable = True, unique = True)
    weight = db.Column(db.Integer, nullable = True)
    max_count = db.Column(db.Integer, default = 1)
    score = db.relationship('Score', back_populates = 'score_type', lazy = True)
    
class Retest(db.Model):
    __tablename__ = 'retest'
    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete = 'CASCADE'), nullable = False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete = 'CASCADE'), nullable = False)
    year_id = db.Column(db.Integer, db.ForeignKey('year.id', ondelete = 'CASCADE'), nullable = False)
    retest_score = db.Column(db.Float)
    students = db.relationship('Students', back_populates = 'retest', lazy = True)
    lesson = db.relationship('Lesson', back_populates = 'retest', lazy = True)
    __table_args__ = (UniqueConstraint('student_id', 'lesson_id', 'year_id', name='stu_les_yea_uniq'),)



