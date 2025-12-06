from app.models import Teachers, Teacher_info, Lesson, Teach_class, Users, Class_room, Tmp_token, LessonTag
from sqlalchemy import func, cast, String, and_
from .base import BaseRepo

class TeacherRepo(BaseRepo):
    def add_user(self, data: dict):
        # username, password, token, name, lesson_id, email, tel, add
        fields = self.filter_context('username', 'password', 'token', 'name', 'lesson_id', 'email', 'tel', 'add', context=data)
        new_user = Users(username = fields['username'], password = fields['password'], role = 'Teacher')
        new_user.tmp_token = [Tmp_token(token = fields['token'])]

        new_teacher = Teachers(name = fields['name'], lesson_id = fields['lesson_id'])
        new_teacher.teacher_info = Teacher_info(email = fields['email'], tel = fields['tel'], add = fields['add'])

        new_teacher.users = new_user
        self.db.session.add(new_teacher)
        self.db.session.flush()
        return new_teacher
    
    def add_teacher(self, data): 
        #user_id, name, lesson_id
        teacher_fields = self.filter_context('user_id', 'name', 'lesson_id', context=data)
        new_teacher = Teachers(**teacher_fields)
        #email, tel, add
        info_fields = self.filter_context('email', 'tel', 'add', context=data)
        new_teacher.teacher_info = Teacher_info(**info_fields)

        self.db.session.add(new_teacher)
        self.db.session.flush()
        return new_teacher

    def show_teachers(self, data: dict):
        fields = self.filter_context('lesson', 'class_room', 'name','year_id', 'grade', 'status', context=data)
        lesson = fields['lesson']
        class_room = fields['class_room']
        name = fields['name']
        grade = fields['grade']

        sub_query = (self.db.session.query(Teach_class.teacher_id.label('teacher_id'),
                                           cast(Teach_class.class_room_id, String).label('class_room_id'),
                                           Class_room.class_room.label('class_room'),
                                           Class_room.grade.label('grade'))
                                                                .join(Teach_class.class_room)
                                                                .join(LessonTag, LessonTag.lesson_id == Teach_class.lesson_id)
                                                                .filter(LessonTag.is_visible == True,
                                                                        Teach_class.year_id == data['year_id'])
                                                                .order_by(Teach_class.class_room_id)
                                                                .subquery())
        query = self.db.session.query(Teachers.id,
                                      Teachers.name,
                                      Lesson.id,
                                      Lesson.lesson,
                                      Class_room.id,
                                      Class_room.class_room,
                                      func.aggregate_strings(sub_query.c.class_room_id, ', '), 
                                      func.aggregate_strings(sub_query.c.class_room, ', '),             
                                      Teacher_info.tel,
                                      Teacher_info.email,
                                      Teacher_info.add,
                                      Teachers.status).join(Lesson)\
                                                      .join(Teacher_info)\
                                                      .outerjoin(sub_query, sub_query.c.teacher_id == Teachers.id)\
                                                      .outerjoin(Class_room, and_(Class_room.teacher_id == Teachers.id,
                                                                                  Class_room.year_id == data['year_id']))                                       
                                                        
        if lesson:
            query = query.filter(Lesson.lesson.ilike(f'%{lesson}%'))

        if name:
            query = query.filter(Teachers.name.ilike(f'%{name}%'))

        if grade:
            query = query.filter(sub_query.c.grade == grade)

        if class_room:
            query = query.filter(sub_query.c.class_room.ilike(f'%{class_room}%'))

        if 'status' in fields and fields['status'] is not None:
            query = query.filter(Teachers.status == fields.get('status'))
            
        return query.order_by(sub_query.c.grade, Lesson.id, Teachers.status).group_by(Teachers.id, Teachers.name, Teachers.status,
                                                                                      Lesson.id, Lesson.lesson,
                                                                                      Class_room.id, Class_room.class_room,
                                                                                      Teacher_info.tel, Teacher_info.email, Teacher_info.add, sub_query.c.grade
                                                                                      ).all()  

    def get_info(self, data: dict):
        return self.db.session.query(Teachers.id,
                                Teachers.name,
                                Teachers.lesson_id,
                                Class_room.id,
                                func.array_agg(Teach_class.class_room_id),
                                Teacher_info.tel,
                                Teacher_info.add,
                                Teacher_info.email,
                                Teach_class.year_id
                                ).outerjoin(Teachers.teach_class)\
                                .join(Teachers.teacher_info)\
                                .outerjoin(Teachers.class_room)\
                                    .filter(Teachers.id == data['teacher_id'])\
                                    .group_by(Teachers.id,
                                            Teachers.name,
                                            Teachers.lesson_id,
                                            Class_room.id,
                                            Teacher_info.tel,
                                            Teacher_info.add,
                                            Teacher_info.email,
                                            Teach_class.year_id
                                            ).first()
    
    def get_teacher_by_user(self, data: dict):
        return self.db.session.query(Teachers).filter(Teachers.user_id == data['user_id']).scalar()

    def get_teacher_by_id(self, data: dict):
        return self.db.session.query(Teachers).filter(Teachers.id == data['teacher_id']).scalar()

    def get_teacher_info_by_teacher(self, data: dict):
        return self.db.session.query(Teacher_info).filter(Teacher_info.teacher_id == data['teacher_id']).scalar()
    
    def delete(self, data: dict):
        pass
    
    def show_teacher_info_by_user(self, data: dict):
        return self.db.session.query(Teachers.name,
                                    Teacher_info.email,
                                    Teacher_info.tel,
                                    Teacher_info.add).outerjoin(Teacher_info).filter(Teachers.user_id == data['user_id']).first()


    def update_teach_class(self, data: dict):
        fields = self.filter_context('year_id', 'teacher_id', 'to_add', 'to_del', context=data)
        to_add = fields['to_add']
        to_del = fields['to_del']

        if to_add:
            for room_id in to_add:
                self.db.session.add(Teach_class(class_room_id = room_id, 
                                                teacher_id = fields['teacher_id']))
        if to_del:
            self.db.session.query(Teach_class).filter(Teach_class.teacher_id == fields['teacher_id'], 
                                    Teach_class.class_room_id.in_(list(to_del))).delete(synchronize_session=False)
            

