from app.models import Class_room, Year, Teachers, Users, Teach_room, Semester, Lesson, Grade
from app.extensions import db

class Class_room_repo:
    def __init__(self, year):
        self.year_id = Year.query.filter(Year.year == year).first().id

    def get_class_room(self, class_room):
        return Class_room.query.filter(Class_room.class_room == class_room, Class_room.year_id == self.year_id).first()
        
    def get_teach_room(self, id):
        data= Teach_room.query.filter(Teach_room.year_id == self.year_id, Teach_room.teacher_id == id).all()
        return [item.teach_room for item in data]
    
    def check_teach_room(self, lesson_id, teach_room):
        return (db.session.query(Teach_room.teach_room, 
                         Teach_room.year_id, 
                         Teachers.lesson_id).join(Teachers, Teachers.id == Teach_room.teacher_id).filter(Teach_room.teach_room == teach_room, 
                                                                                                        Teachers.lesson_id == lesson_id,
                                                                                                        Teach_room.year_id == self.year_id).first())
       
    def add_class_room(self, class_room):
        grade_id = Grade.query.filter(Grade.grade == class_room[0,1]).first().id
        db.session.add(Class_room(class_room = class_room, year_id = self.year_id, grade_id = grade_id))

    def assign_teach_rooms(self, teacher_id, teach_room):
        if isinstance(teach_room, str):
            teach_room = [teach_room]

        for room in teach_room:
            data = self.get_class_room(room)
            
            new_teach_room = Teach_room(teacher_id = teacher_id, teach_room = data.id, year_id = self.year_id)
            db.session.add(new_teach_room)

    def show_class_room(self, class_room):
        query = Class_room.query
        if class_room:
            query = query.filter(Class_room.class_room.ilike(f'%{class_room}%'))

        query = query.order_by(Class_room.class_room).all()
        return [class_room.class_room for class_room in query]
    
    def show_teach_room(self, id):
        data = Teach_room.query.join(Class_room).filter(Teach_room.teacher_id == id, Teach_room.year_id == self.year_id).all()
        return [teach_room.class_room for teach_room in data]
    
    def update_teach_room(self, id, to_del, to_add):
        if to_add:
            for room_id in to_add:
                db.session.add(Teach_room(teach_room = room_id, 
                                        year_id = self.year_id, 
                                        teacher_id = id))
        if to_del:
            Teach_room.query.filter(Teach_room.teacher_id == id, 
                                    Teach_room.year_id == self.year_id, 
                                    Teach_room.teach_room.in_(list(to_del))).delete(synchronize_session=False)

class Academic_repo:
    class Get_repo:
        @staticmethod
        def get_year(year):
            return (Year.query.filter(Year.year == year).first())
            
        @staticmethod
        def get_lesson(lesson):
            return (Lesson.query.filter(Lesson.lesson == lesson).first())
        
        @staticmethod
        def get_semester(semester):
            return (Semester.query.filter(Semester.semester == semester).first())
        
        @staticmethod
        def get_grade(grade):
            return (Grade.query.filter(Grade.grade == grade).first())
    class Add_repo:
        @staticmethod
        def add_year(year):
            db.session.add(Year(year = year))

        @staticmethod
        def add_semester(semester, year_id):
            db.session.add(Semester(semester = semester, year_id = year_id))

        @staticmethod
        def add_grade(grade):
            db.session.add(Grade(grade = grade))

        @staticmethod
        def add_lesson(lesson):
            db.session.add(Lesson(lesson = lesson))
    class Show_repo:
        @staticmethod
        def show_year(year = None):
            query = Year.query
            if year:
                query = query.filter(Year.year.ilike(f'%{year}%'))

            query = query.all()
            return [data.year for data in query]

        @staticmethod
        def show_semester(semester = None):
            query = Semester.query
            if semester:
                query = query.filter(Semester.semester.ilike(f'%{semester}%'))
            
            query = query.all()
            return [data.semester for data in query]

        @staticmethod
        def show_lesson(lesson = None):
            query = db.session.query(Lesson.lesson)
            if lesson:
                query = query.filter(Lesson.lesson.ilike(f'%{lesson}%'))
                
            query = query.all()
            return [data.lesson for data in query]
        
        @staticmethod
        def show_grade(grade = None):
            query = Grade.query

            if grade:
                query = query.filter(Grade.grade.ilike(f'%{grade}%'))
            
            query = query.all()
            return [data.grade for data in query]