from app.models import Class_room, Year, Teachers, Teach_class, Semester, Lesson, Grade, Period, Student_Class
from .base import BaseRepo
from sqlalchemy import select

class AcademicCheckRepo(BaseRepo):
    def year(self, data: dict):
        return self.obj_by_obj_name(Year, Year.year, data['year'])
            
    def lesson(self, data: dict):
        return self.obj_by_obj_name(Lesson, Lesson.lesson, data['lesson'])
        
    def grade(self, data: dict):
        return self.obj_by_obj_name(Grade, Grade.grade, data['grade'])
           
    def semester(self, data: dict):
        return self.obj_by_obj_name(Semester, Semester.semester, data['semester'])
    
    def class_room(self, data: dict):
        return self.db.session.query(Class_room).filter(Class_room.class_room == data['class_room'], 
                                                        Class_room.year_id == data['year_id']).scalar()

class AcademicGetRepo(BaseRepo):
    def year_by_id(self, data: dict):
        fields = self.filter_context('year_id', context=data)
        return self.obj_by_obj_id(Year, fields['year_id'])
    
    def grade_by_id(self, data: dict):
        print('chekc',data)
        return self.db.session.query(Grade).filter(Grade.id == data['grade_id']).first()
        return self.obj_by_obj_id(Grade, 1)

    def lesson_by_id(self, data: dict):
        return self.obj_by_obj_id(Lesson, data['lesson_id'])
    
    def semester_by_id(self, data: dict):
        return self.obj_by_obj_id(Semester, data['semester_id'])
    
    def class_room_by_id(self, data: dict):
        return self.db.session.query(Class_room).filter(Class_room.id == data['class_room_id'],
                                                        Class_room.year_id == data['year_id']).first()
    
    def get_period_id(self, data):
        return self.db.session.query(Period.id).filter(Period.year_id == data['year_id'],
                                                       Period.semester_id == data['semester_id']).scalar()
    
    def class_room_by_teacher_id(self, data: dict):
        return self.db.session.query(Class_room).filter(Class_room.teacher_id == data['teacher_id'],
                                                        Class_room.year_id == data['year_id']).first()
    
    def class_room_by_grade_id(self, data: dict):
        return self.db.session.query(Class_room.id).filter(Class_room.grade_id >= data['grade_id']).all()
    
    def teach_class_by_teacher_id(self, data: dict):
        query = self.db.session.query(Teach_class).join(Class_room).filter(Class_room.year_id == data['year_id'],
                                                                            Teach_class.lesson_id == data['lesson_id'],
                                                                            Teach_class.teacher_id == data['teacher_id']).all()
        return query
    
    def teach_class_id_by_teacher_id(self, data: dict):
        fields = self.filter_context('year_id', 'teacher_id', 'lesson_id', context=data)

        return self.db.session.scalars(select(Teach_class.class_room_id).join(Class_room).filter(Class_room.year_id == fields['year_id'],
                                                                                          Teach_class.lesson_id == fields['lesson_id'],
                                                                                          Teach_class.teacher_id == fields['teacher_id'])).all()

    def teach_class_by_class_room_id(self, data: dict):
        fields = self.filter_context('teach_class', 'lesson_id', context=data)
        return self.db.session.query(Teach_class).filter(Teach_class.class_room_id.in_(fields['teach_class']),
                                                          Teach_class.lesson_id == fields['lesson_id']).all()
    
    def assign_student_class_by_student_id(self, data):
        for student_id in data['student_ids']:
            student_class = self.db.session.query(Student_Class).filter(Student_Class.student_id == student_id).first()
            student_class.class_room_id = data['class_room_id']



class AcademicAddRepo(BaseRepo):
    def year(self, data: dict):
        # year
        new_year = (Year(**data))
        semester_ids = self.db.session.scalars(select(Semester.id)).all()
        self.db.session.add(new_year)
        self.db.session.flush()
        for semester_id in semester_ids:
            new_period = Period(year_id = new_year.id, semester_id = semester_id)
            self.db.session.add(new_period)

    def semester(self, data: dict):
        # semester, year_id
        self.db.session.add(Semester(**data))

    def grade(self, data: dict):
        # grade
        self.db.session.add(Grade(**data))

    def lesson(self, data: dict):
        # lesson
        fields = self.filter_context('lesson', 'grade_id', 'year_id', context=data)
        new_lesson = Lesson(**fields)
        self.db.session.add(new_lesson)
        self.db.session.flush()
        for room_id in data['class_room_id']:
            self.db.session.add(Teach_class(lesson_id = new_lesson.id,
                                            class_room_id = room_id[0],
                                            year_id = fields['year_id']))
            # self.db.session.add(Class_lesson(lesson_id = new_lesson.id, 
            #                                  class_room_id = room_id[0], 
            #                                  year_id = fields['year_id']))

    def class_room(self, data: dict):
        fields = self.filter_context('class_room', 'year_id', context=data)
        grade_id = self.db.session.query(Grade).filter(Grade.grade == fields['class_room'][:2]).first().id
        self.db.session.add(Class_room(class_room = fields['class_room'], year_id = fields['year_id'], grade_id = grade_id))

class AcademicShowRepo(BaseRepo):
    def year(self, data: dict):
        query = self.db.session.query(Year.id, Year.year)
        if data['year']:
            query = query.filter(Year.year.ilike(f'%{data['year']}%'))
        if data['is_active']:
            query = query.filter(Year.is_active == data['is_active'])
   
        return query.order_by(Year.is_active.desc()).all()
        
    def semester(self, data: dict):
        semester = data['semester']
        query = self.db.session.query(Semester.id, Semester.semester)
        if semester:
            query = query.filter(Semester.semester.ilike(f'%{semester}%'))
        
        return query.all()
        
    def lesson(self, data: dict):
        fields = self.filter_context('lesson', 'grade_id', 'year_id', context=data)

        query = self.db.session.query(Lesson.id, Lesson.lesson, Grade.grade, Grade.id).outerjoin(Grade)
        if fields['lesson']:
            query = query.filter(Lesson.lesson.ilike(f'%{fields['lesson']}%'))
        
        if fields['grade_id']:
            query = query.filter(Lesson.grade_id <= fields['grade_id'])

        if fields['year_id']:
            query = query.filter(Lesson.year_id == fields['year_id'])

        return query.order_by(Grade.grade).all()            

    def lesson_by_id(self, data: dict):
        teacher_id = data['teacher_id']
        lesson = data['lesson']
        query = self.db.session.query(Lesson.id,
                                Lesson.lesson,
                                Teachers.id).join(Teachers)
        if lesson:
            query = query.filter(Lesson.lesson.ilike(f'%{lesson}%'))
        
        if teacher_id:
            query = query.filter(Teachers.id == teacher_id)
            
        return query.first()
                
    def grade(self, data: dict):
        grade = data['grade']
        query = self.db.session.query(Grade.id, Grade.grade)
        if grade:
            query = query.filter(Grade.grade.ilike(f'%{grade}%'))
        
        return query.all()
    
    def class_room(self, data: dict):
        fields = self.filter_context('class_room', 'year_id', 'grade_id', context=data)
        query = self.db.session.query(Class_room.id, Class_room.class_room, Class_room.grade_id, Class_room.teacher_id)

        if fields['class_room']:
            query = query.filter(Class_room.class_room.ilike(f'%{fields['class_room']}%'))

        if fields['grade_id']:
            query = query.filter(Class_room.grade_id == fields['grade_id'])
        
        if fields['year_id']:
            query = query.filter(Class_room.year_id == fields['year_id'])

        return query.order_by(Class_room.class_room).all()
    
    def teach_class(self, data: dict):
        fields = self.filter_context('teacher_id', 'year_id', context=data)
        teacher_id = fields['teacher_id']
        year_id = fields['year_id']
        query = self.db.session.query(Teach_class.class_room,
                                     Class_room.class_room).join(Class_room)
        if teacher_id: 
            query = query.filter(Teach_class.teacher_id == teacher_id)

        if year_id:
            query = query.filter(Teach_class.year_id == year_id)
        
        return query.all()
    
    def teach_class_with_teacher_id_by_lesson_id(self, data: dict):
        fields = self.filter_context('year_id', 'lesson_id', context=data)
        return self.db.session.query(Teach_class.class_room_id,
                                     Teach_class.lesson_id,
                                     Teach_class.teacher_id,
                                     Class_room.class_room,
                                     Teachers.name).outerjoin(Teach_class.class_room)\
                                                   .outerjoin(Teach_class.teachers).filter(Teach_class.lesson_id == fields['lesson_id'],
                                                                                           Class_room.year_id == fields['year_id'])\
                                                                                          .order_by(Class_room.class_room).all()
            
class AcademicUpdateRepo(BaseRepo):            
    def class_lesson_by_lesson_id(self, data: dict):
        fields = self.filter_context('class_room_id', 'lesson_id', 'year_id', context=data)

        self.db.session.query(Class_lesson).filter(Class_lesson.lesson_id == fields['lesson_id'],
                                                   Class_lesson.year_id == fields['year_id']).delete(synchronize_session=False)
        
        teach_to_delete = self.db.session.query(Teach_class).join(Class_room).filter(Teach_class.lesson_id == fields['lesson_id'],
                                                                   Class_room.year_id == fields['year_id']).all()
        for i in teach_to_delete:
            self.db.session.delete(i)
        
        for room_id in fields['class_room_id']:
            self.db.session.add(Class_lesson(lesson_id = fields['lesson_id'],
                                             class_room_id = room_id,
                                             year_id = fields['year_id']))
            
            self.db.session.add(Teach_class(lesson_id = fields['lesson_id'],
                                            class_room_id = room_id,
                                            year_id = fields['year_id']))
     
    def update_year_status(self):
        self.db.session.query(Year).filter(Year.is_active == True).update({Year.is_active: False})