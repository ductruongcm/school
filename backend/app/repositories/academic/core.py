from app.models import Class_room, Year, Teachers, Teach_class, Semester, Lesson, Grade, Period, LessonTag, Score_Type, Student_Year_Summary, Students
from ..base import BaseRepo
from sqlalchemy import select, func
from datetime import date

class AcademicGetRepo(BaseRepo):
    def get_year_by_year_code(self, data: dict):
        return self.db.session.query(Year).filter(Year.year_code == data['year_code']).first()
    
    def get_prev_year_id(self, data: dict):
        return self.db.session.query(Year.id).filter(Year.year_code.like(f"%{data['year_code']}")).scalar()
    
    def get_new_year_id(self, data):
        return self.db.session.query(Year.id).filter(Year.year_code.like(f'{data}%')).scalar()
            
    def check_lesson(self, data: dict):
        return self.obj_by_obj_name(Lesson, Lesson.lesson, data['lesson'])
        
    def get_grade_by_grade(self, data: dict):
        return self.db.session.query(Grade).filter(Grade.grade == data['grade']).first()
        
    def get_grade_by_class_room(self, data: dict):
        return self.db.session.query(Class_room.grade).filter(Class_room.id == data['class_room_id']).scalar()
    
    def get_grade_by_lesson(self, data: dict):
        return self.db.session.query(Lesson.grade).filter(Lesson.id == data['lesson_id']).scalar()
           
    def check_semester(self, data: dict):
        return self.obj_by_obj_name(Semester, Semester.semester, data['semester'])
    
    def check_class_room(self, data: dict):
        return self.db.session.query(Class_room).filter(Class_room.class_room == data['class_room'], 
                                                        Class_room.year_id == data['year_id']).scalar()
    
    def get_score_type(self, data: dict):
        return self.db.session.query(Score_Type).filter(Score_Type.score_type == data['score_type']).first()
    
    def get_score_type_by_id(self, data: dict):
        return self.db.session.query(Score_Type).filter(Score_Type.id == data['score_type_id']).first()

    def get_year_by_id(self, data: dict):
        fields = self.filter_context('year_id', context=data)
        return self.obj_by_obj_id(Year, fields['year_id'])
    
    def get_lesson_tag_by_lesson(self, data: dict):
        return self.db.session.query(LessonTag).filter(LessonTag.lesson_id==data['lesson_id']).first()
    
    def get_semester_by_id(self, data: dict):
        return self.obj_by_obj_id(Semester, data['semester_id'])
    
    def get_class_room_by_id(self, data: dict):
        return self.db.session.query(Class_room).filter(Class_room.id == data['class_room_id']).first()
    
    def get_period_id(self, data):
        return self.db.session.query(Period.id).filter(Period.year_id == data['year_id'],
                                                       Period.semester_id == data['semester_id']).scalar()
    
    def get_class_room_by_year(self, data):
        return self.db.session.query(Class_room).filter(Class_room.year_id == data['year_id']).all()
    
    def get_class_rooms_by_grade(self, data: dict):
        return self.db.session.scalars(select(Class_room).filter(Class_room.grade == data['grade'])).all()
    
    def get_class_room_by_teacher_id(self, data: dict):
        return self.db.session.query(Class_room).filter(Class_room.teacher_id == data['teacher_id'],
                                                        Class_room.year_id == data['year_id']).first()

    def get_teaching_class_by_class_rooms(self, data: dict):
        fields = self.filter_context('teaching_class_ids', 'lesson_id', 'year_id', context=data)
        return self.db.session.query(Teach_class).filter(Teach_class.class_room_id.in_(fields['teaching_class_ids']),
                                                         Teach_class.lesson_id == fields['lesson_id'],
                                                         Teach_class.year_id == fields['year_id']).all()
    
    def get_teaching_class_by_class_room_year_general_folder(self, data):
        return (self.db.session.query(Teach_class)
                .join(LessonTag, LessonTag.lesson_id == Teach_class.lesson_id)
                .filter(Teach_class.year_id == data['year_id'],
                        Teach_class.class_room_id == data['class_room_id'],
                        LessonTag.is_folder == True, 
                        LessonTag.is_visible == False).scalar())
    
    def get_general_folder_id(self):
        return self.db.session.query(Lesson.id).join(Lesson.lessontag).filter(LessonTag.is_folder == True, 
                                                                              LessonTag.is_visible == False).scalar()
    
    def get_class_lessons_by_year(self, data):
        return (self.db.session.query(Class_room.id, Lesson.id)
                               .join(Lesson, Class_room.grade >= Lesson.grade)
                               .join(Lesson.lessontag)
                               .filter(Class_room.year_id == data['year_id'],
                                       LessonTag.is_folder == True).all())
    
    def get_lessons_by_grade_and_is_visible(self, data):
        rows = self.db.session.query(func.jsonb_build_object(Lesson.id, Lesson.lesson)).join(LessonTag.lesson).filter(Lesson.grade <= data['grade'],
                                                                                                                      LessonTag.is_visible == True).all()
        return [row[0] for row in rows]

    def get_lesson_ids_by_grade_and_is_visible(self, data):
        return (self.db.session.scalars(select(Lesson.id).join(Lesson.lessontag).filter(LessonTag.is_visible == True,
                                                                                        Lesson.grade <= data['grade'])).all())
    
    def get_lesson_by_id(self, data: dict):
        return self.db.session.query(Lesson).filter(Lesson.id == data['lesson_id']).scalar()
    
    def get_period_ids_by_year(self, data):
        return self.db.session.scalars(select(Period.id).filter(Period.year_id == data['year_id'])).all()

class AcademicAddRepo(BaseRepo):
    def insert_year(self, data: dict):
        # year
        new_year = (Year(**data))
        self.db.session.add(new_year)
        self.db.session.flush()
        return new_year

    def insert_semester(self, data: dict):
        # semester
        self.db.session.add(Semester(**data))

    def insert_period(self, data: dict):
        self.db.session.add(Period(**data))

    def insert_grade(self, data: dict):
        # grade
        self.db.session.add(Grade(**data))

    def insert_lesson(self, data: dict):
        # lesson
        fields = self.filter_context('lesson', 'grade', context=data)
        new_lesson = Lesson(**fields)

        fields = self.filter_context('is_visible', 'is_folder', 'is_schedule', context=data)
        new_lesson.lessontag = [LessonTag(**fields)]
        self.db.session.add(new_lesson)

        self.db.session.flush()
        return new_lesson

    def insert_class_room(self, data: dict):
        fields = self.filter_context('class_room', 'year_id', context=data)
        grade = fields['class_room'][:2]
        self.db.session.add(Class_room(class_room = fields['class_room'], year_id = fields['year_id'], grade = grade))

    def insert_score_types(self, data:dict):
        self.db.session.add(Score_Type(**data))

class AcademicShowRepo(BaseRepo):
    def show_years(self, data: dict):
        query = self.db.session.query(Year.id, Year.year_code)

        if data.get('is_active'):
            query = query.filter(Year.is_active == data['is_active'])
   
        return query.order_by(Year.is_active.desc()).all()
    
    def show_years_for_student(self, data):
        return (self.db.session.query(Student_Year_Summary.year_id, Year.year_code)
                               .join(Student_Year_Summary, Student_Year_Summary.year_id == Year.id)
                               .join(Student_Year_Summary.students)
                               .filter(Students.user_id == data['user_id'])
                               .order_by(Year.id)
                               .all())
    
    def show_prev_year_code(self):
        return self.db.session.query(Year.id, Year.year_code).filter(Year.end_date < date.today()).order_by(Year.year_code.desc()).limit(1).first()
        
    def show_semesters(self, data: dict):
        query = self.db.session.query(Semester.id, Semester.semester, Semester.is_active)

        # if data['semester']:
        #     query = query.filter(Semester.semester.ilike(f'%{data['semester']}%'))
        if data.get('is_active'):
            query = query.filter(Semester.is_active == data['is_active'])
        
        return query.order_by(Semester.is_active.desc()).all()
        
    def show_lessons(self, data: dict):
        query = self.db.session.query(Lesson.id, Lesson.lesson, 
                                      Grade.grade, 
                                      LessonTag.is_visible, LessonTag.is_folder, LessonTag.is_schedule).join(Grade).join(LessonTag)
        
        if data['grade']:
            query = query.filter(Lesson.grade <= data['grade'])
        
        if data['is_visible']:
            query = query.filter(LessonTag.is_visible == data['is_visible'])

        if data['is_folder']:
            query = query.filter(LessonTag.is_folder == data['is_folder'])

        if data['is_schedule']:
            query = query.filter(LessonTag.is_schedule == data['is_schedule'])

        return query.filter(Lesson.status == True).order_by(Lesson.id).all()            

    def show_lesson_by_user(self, data: dict):
        return self.db.session.query(Lesson.id,
                                     Lesson.lesson).join(Lesson.teachers).filter(Teachers.user_id == data['user_id']).all()
                     
    def show_grades(self, data: dict):
        query = self.db.session.query(Grade.grade, Grade.grade_status)

        if data.get('grade_status'):
            query = query.filter(Grade.grade_status == data.get('grade_status'))

        return query.order_by(Grade.grade).all()
    
    def show_class_room_by_year_and_grade(self, data: dict):
        query = self.db.session.query(Class_room.id, Class_room.class_room, Class_room.grade)

        if data.get('grade'):
            query = query.filter(Class_room.grade == data['grade'])
        
        if data.get('year_id'):
            query = query.filter(Class_room.year_id == data['year_id'])

        return query.order_by(Class_room.class_room).all()
    
    def show_teach_class_by_user(self, data: dict):
        fields = self.filter_context('user_id', 'year_id', context=data)
        year_id = fields['year_id']
        query = self.db.session.query(Teach_class.class_room_id,
                                      Class_room.class_room,
                                      Class_room.grade).join(Teach_class.class_room)\
                                                       .join(Teach_class.teachers).filter(Teachers.user_id == fields['user_id'])

        if year_id:
            query = query.filter(Teach_class.year_id == year_id)
        
        return query.distinct(Teach_class.class_room_id).order_by(Teach_class.class_room_id).all()
        
    def teach_class_with_teacher_id_by_lesson_id(self, data: dict):
        fields = self.filter_context('year_id', 'lesson_id', context=data)
        return self.db.session.query(Teach_class.class_room_id,
                                     Teach_class.teacher_id,
                                     Class_room.class_room,
                                     ).outerjoin(Teach_class.class_room).filter(Teach_class.lesson_id == fields['lesson_id'],
                                                                                Teach_class.year_id == fields['year_id']).order_by(Class_room.class_room).all()
    
    def show_lessons_by_grade(self, data):
        query = self.db.session.query(Lesson.id, Lesson.lesson).join(Lesson.lessontag).filter(LessonTag.is_visible == True)

        if data['grade']:
            query = query.filter(Lesson.grade <= data['grade'])
        
        return query.order_by(Lesson.lesson).all()
    
    def show_score_types(self):
        return self.db.session.query(Score_Type.id, 
                                     Score_Type.score_type,
                                     Score_Type.weight).all()
