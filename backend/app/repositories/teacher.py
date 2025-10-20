from app.models import Teachers, Teacher_info, Lesson, Teach_class, Users, Class_room, Tmp_token
from sqlalchemy import text, func, cast, String
from sqlalchemy.orm import aliased
from .base import BaseRepo

class TeachersRepo(BaseRepo):
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

    def show_teacher(self, data: dict):
        fields = self.filter_context('lesson', 'class_room', 'name','year_id', 'grade_id', context=data)
        lesson = fields['lesson']
        class_room = fields['class_room']
        name = fields['name']
        year_id = fields['year_id']
        grade_id = fields['grade_id']

        Teachclass = aliased(Class_room)                                                    #Tạo 1 bảng phụ để lấy thông tin class_room
        query = self.db.session.query(Teachers.id,
                                Teachers.name,
                                Lesson.id,
                                Lesson.lesson,
                                Class_room.id,
                                Class_room.class_room,
                                func.array_agg(Teachclass.id),
                                func.string_agg(cast(Teachclass.class_room, String),        #func.string_agg(str, ', ') để gộp row thành chuỗi với type str - cast(int, String) chuyển int về str
                                text("', ' ORDER BY class_room_1.class_room")),                 
                                Teacher_info.tel,
                                Teacher_info.email,
                                Teacher_info.add,
                                Teachers.status).join(Lesson)\
                                                .outerjoin(Class_room, Class_room.teacher_id == Teachers.id)\
                                                .outerjoin(Teach_class, Teach_class.teacher_id == Teachers.id)\
                                                .outerjoin(Teachclass, Teachclass.id == Teach_class.class_room_id)\
                                                .join(Teacher_info)
        
        if lesson:
            query = query.filter(Lesson.lesson.ilike(f'%{lesson}%'))
        if class_room:
            query = query.filter(Teachclass.class_room.ilike(f'%{class_room}%'))
        if name:
            query = query.filter(Teachers.name.ilike(f'%{name}%'))
        if year_id:
            query = query.filter(Teachclass.year_id == year_id)
        if grade_id:
            query = query.filter(Teachclass.grade_id == grade_id)
        
        return query.order_by(Class_room.class_room,
                              Teachers.status).group_by(Teachers.id, 
                                                        Teachers.name, 
                                                        Lesson.id,
                                                        Lesson.lesson, 
                                                        Class_room.id,
                                                        Class_room.class_room, 
                                                        Teacher_info.tel, 
                                                        Teacher_info.email, 
                                                        Teacher_info.add).all()  

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
                                    .filter(Teachers.id == data['teacher_id'],
                                            Teach_class.year_id == data['year_id'])\
                                    .group_by(Teachers.id,
                                            Teachers.name,
                                            Teachers.lesson_id,
                                            Class_room.id,
                                            Teacher_info.tel,
                                            Teacher_info.add,
                                            Teacher_info.email,
                                            Teach_class.year_id
                                            ).first()
        
    def get_teacher(self, data: dict):
        return self.db.session.query(Teachers).filter(Teachers.id == data['teacher_id']).first()

    def get_teacher_info(self, data: dict):
        return self.db.session.query(Teacher_info).filter(Teacher_info.teacher_id == data['teacher_id']).first()
    
    def delete(self, data: dict):
        pass
    
    def check_teach_class(self, data: dict):    
        fields = self.filter_context('teach_class', 'lesson_id', 'year_id', context=data)
        query = self.db.session.query(Teach_class).filter(Teach_class.class_room_id.in_(fields['teach_class']), 
                                                          Teach_class.lesson_id == fields['lesson_id'],
                                                          Teach_class.year_id == fields['year_id'])
        return [check.teacher_id for check in query.all()]
    
    def assign_teach_class(self, data: dict):
        fields = self.filter_context('teach_class', 'teacher_id', 'year_id', 'lesson_id', context=data)
        teach_class = fields['teach_class']
        if isinstance(teach_class, str):
            teach_class = [teach_class]

        for room in teach_class:
            new_teach_class = Teach_class(teacher_id = fields['teacher_id'], 
                                          class_room_id = room, 
                                          lesson_id = fields['lesson_id'], 
                                          year_id = fields['year_id'])
            self.db.session.add(new_teach_class)

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
            

