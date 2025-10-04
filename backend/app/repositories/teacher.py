from app.models import Teachers, Teacher_info, Lesson, Teach_room, Users, Class_room, Tmp_token, Year
from app.extensions import db
from sqlalchemy import text, func, cast, String
from sqlalchemy.orm import aliased


class TeachersRepositories:
    @staticmethod
    def add_user(username, password, token, name, lesson_id, email, tel, add):
        new_user = Users(username = username, password = password, role = 'Teacher')
        new_user.tmp_token = [Tmp_token(token = token)]

        new_teacher = Teachers(name = name, lesson_id = lesson_id)
        new_teacher.teacher_info = Teacher_info(email = email, tel = tel, add = add)

        new_teacher.users = new_user
        db.session.add(new_teacher)
        db.session.flush()
        return new_teacher

    @staticmethod
    def show_teacher(lesson = None, class_room = None, name = None):
        Teachclass = aliased(Class_room)                                                    #Tạo 1 bảng phụ để lấy thông tin class_room
        query = db.session.query(Teachers.id,
                                Teachers.name,
                                Lesson.lesson,
                                Class_room.class_room,
                                func.string_agg(cast(Teachclass.class_room, String),        #func.string_agg(str, ', ') để gộp row thành chuỗi với type str - cast(int, String) chuyển int về str
                                text("', ' ORDER BY class_room_1.class_room")),                 
                                Teacher_info.tel,
                                Teacher_info.email,
                                Teacher_info.add).join(Lesson)\
                                                .outerjoin(Class_room, Class_room.teacher_id == Teachers.id)\
                                                .outerjoin(Teach_room, Teach_room.teacher_id == Teachers.id)\
                                                .outerjoin(Teachclass, Teachclass.id == Teach_room.teach_room).join(Teacher_info)
        
        if lesson:
            query = query.filter(Lesson.lesson.ilike(f'%{lesson}%'), Teachers.status == True)
        if class_room:
            query = query.filter(Teachclass.class_room.ilike(f'%{class_room}%'), Teachers.status == True)
        if name:
            query = query.filter(Teachers.name.ilike(f'%{name}%'), Teachers.status == True)
        
        return query.order_by(Class_room.class_room).group_by(Teachers.id, 
                                                              Teachers.name, 
                                                              Lesson.lesson, 
                                                              Class_room.class_room, 
                                                              Teacher_info.tel, 
                                                              Teacher_info.email, 
                                                              Teacher_info.add).all()  

    class Get_repo:
        @staticmethod
        def get_info(id, year):
            Teachclass = aliased(Class_room)
            data = db.session.query(Teachers.id,
                                    Teachers.name,
                                    Lesson.lesson,
                                    Class_room.class_room,
                                    Class_room.id,
                                    func.aggregate_strings(cast(Teachclass.class_room, String), ', '),
                                    Teacher_info.tel,
                                    Teacher_info.add,
                                    Teacher_info.email
                                    ).join(Lesson)\
                                    .outerjoin(Class_room, Class_room.teacher_id == id)\
                                    .outerjoin(Teach_room, Teach_room.teacher_id == id)\
                                    .outerjoin(Teachclass, Teach_room.teach_room == Teachclass.id)\
                                    .join(Teacher_info).filter(Teachers.id == id)\
                                        .group_by(Teachers.id,
                                                Teachers.name,
                                                Lesson.lesson,
                                                Class_room.class_room,
                                                Class_room.id,
                                                Teacher_info.tel,
                                                Teacher_info.add,
                                                Teacher_info.email
                                                ).first()
            return data

        @staticmethod
        def get_teacher(id):
            return Teachers.query.filter(Teachers.id == id).first()

        @staticmethod
        def get_teacher_info(id):
            return Teacher_info.query.filter(Teacher_info.teacher_id == id).first()
    
def db_update_info(id, name = None, lesson = None, class_room = None, tel = None, add = None, email = None):
    #lấy thông tin và update
    teacher = Teachers.query.filter(Teachers.id == id).first()
    info = Teacher_info.query.filter(Teacher_info.teacher_id == id).first()
    #update name
    if name:
        teacher.name = name
    #update lesson
    if lesson:
        new_lesson = Lesson.query.filter(Lesson.lesson == lesson).first().id
        teacher.lesson_id = new_lesson
    #update class_room
    if class_room:
        new_class_room = Class_room.query.filter(Class_room.class_room == class_room).first().id
        teacher.class_room_id = new_class_room
    #update tel
    if tel:
        info.tel = tel
    #update add
    if add:
        info.add = add
    #update email
    if email:
        info.email = email
    db.session.commit()


