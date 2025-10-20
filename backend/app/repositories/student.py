from app.extensions import db
from .base import BaseRepo
from sqlalchemy import func, select
from app.models import Students, Class_room, Users, Score, Lesson, Student_info, Student_Lesson_Period, Student_Class, Period, Grade

class StudentsRepo(BaseRepo):
    def add_student(self, data):
        student = Students(name = data['name'])
     
        student.student_info = [Student_info(tel = data['tel'],
                                            add = data['add'],
                                            gender = data['gender'],
                                            BOD = data['bod'])]
        self.db.session.add(student)
        self.db.session.flush()
        return student
    
    def student_last_code(self):
        last_code = self.db.session.query(func.max(Students.student_code)).scalar()
        if not last_code:
            next_num = 1
        else:
            last_num = int(last_code[-4:])
            next_num = last_num + 1
        return next_num
    
    def add_user(self, data):
        user = Users(**data)
        self.db.session.add(user)
        self.db.session.flush()
        return user

    def check_student_code(self, data):
        return self.db.session.query(Students).filter(Students.student_code == data).first()
    
    def get_lessons_id_by_grade_id(self, data):
        fields = self.filter_context('grade_id', 'year_id', context=data)
        return self.db.session.scalars(select(Lesson.id).filter(Lesson.year_id == fields['year_id'],
                                                       Lesson.grade_id <= fields['grade_id'])).all()
    
    def get_period_id(self, data: dict):
        fields = self.filter_context('year_id', 'semester_id', context=data)
        return self.db.session.query(Period.id).filter(Period.year_id == fields['year_id'],
                                                       Period.semester_id == fields['semester_id']).scalar()

    def student_lesson_period(self, data: dict):
        fields = self.filter_context('student_id', 'lessons_id', context=data)
        for lesson_id in fields['lessons_id']:
            student_lesson = Student_Lesson_Period(student_id = fields['student_id'],
                                                   lesson_id = lesson_id)
            student_lesson.score = [Score()]
            self.db.session.add(student_lesson)

    def student_class(self, data: dict):
        fields = self.filter_context('class_room_id', 'student_id', 'grade_id', 'year_id', context=data)
        self.db.session.add(Student_Class(**fields))

    def show_student_by_grade(self, data):
        query = self.db.session.query(Students.id,
                                      Students.name,
                                      Student_info.tel,
                                      Student_info.add,
                                      Grade.grade).join(Students.student_info)\
                                                  .join(Students.student_class)\
                                                  .join(Grade, Student_Class.grade_id == Grade.id)
        if data['grade_id']:
            query = query.filter(Student_Class.grade_id == data['grade_id'])
        
        return query.filter(Student_Class.class_room_id == None).all()
    
# def db_add_student(name, current_class_room, tel, add, role, year):
#     class_room = Class_room.query.filter(Class_room.class_room == current_class_room).first()
#     new_student = Students(name = name, class_room_id = class_room.id)
#     db.session.add(new_student)
#     db.session.flush()
#     username = generate_student_id(year, current_class_room) 
#     if new_student.id < 10:
#         username = f'{username}0{new_student.id}'
#     else:
#         username = f'{username}{new_student.id}'
#     # password = generate_password_hash(generate_password(length = 32))
#     new_student.student_id = username
#     # new_user = Users(username = username, password = password, role = role)
#     # new_info = Student_info(user_id = new_user.id, name = name, tel = tel, add = add)
#     # db.session.add_all([new_user, new_info])
#     db.session.flush()
#     # new_student.info_id = new_info.id
#     db.session.commit()

def db_show_student(current_class_room): 
    rows = db.session.query(Students.id,
                            Students.name, 
                            Student_info.tel, 
                            Student_info.add).join(Students).join(Class_room).filter(current_class_room == Class_room.class_room).order_by(Students.name).all()
    keys = ['id', 'name', 'tel', 'add']

    return [dict(zip(keys, row)) for row in rows]

def db_update_info(id, name = None, tel = None, add = None):
    student = Students.query.filter(Students.id == id).first()
    info = Student_info.query.filter(Student_info.id == student.info_id).first()
    if name:
        student.name = name
        info.name = name
    if tel:
        info.tel = tel
    if add:
        info.add = add
    db.session.commit()

def db_show_score(class_room, lesson):
    rows = db.session.query(Students.name,
                           Score.score_oral,
                           Score.score_15m,
                           Score.score_45m,
                           Score.score_final,
                           Score.total,
                           Score.remark).join(Class_room, Class_room.id == Students.class_room_id)\
                                        .outerjoin(Score, Score.class_room_id == Class_room.id)\
                                        .join(Lesson, Lesson.id == Score.lesson_id).filter(Class_room.class_room == class_room, Lesson.lesson == lesson).all()
    keys = ['name', 'score_oral', 'score_15m', 'score_45m', 'score_45m', 'score_final', 'total', 'remark']
    return [dict(zip(keys, row)) for row in rows]

   