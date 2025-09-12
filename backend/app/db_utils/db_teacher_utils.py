from app.schemas.teacher_schemas import Teachers, Infos_teacher, Lesson
from app.schemas.class_room_schemas import Class_room
from app.extensions import db

def db_add_lesson(lesson):
    new_lesson = Lesson(lesson = lesson)
    db.session.add(new_lesson)
    db.session.commit()

def db_add_teacher(name, current_lesson, current_class_room, tel, add, email):
    lesson = Lesson.query.filter(Lesson.lesson == current_lesson).first()
    class_room = Class_room.query.filter(Class_room.class_room == current_class_room).first()
    new_teacher = Teachers(name = name, lesson_id = lesson.id, class_room_id = class_room.id)
    db.session.add(new_teacher)
    db.session.flush()
    new_teacher_info = Infos_teacher(teacher_id = new_teacher.id, email = email, tel = tel, add = add)
    db.session.add(new_teacher_info)
    db.session.commit()

def db_show_teacher(lesson = None, class_room = None, name = None):
    #Show table bằng join các tables đồng thời search
    #Chỉ join, không chốt table để search
    query = Teachers.query.with_entities(Teachers.id,
                        Teachers.name,
                        Lesson.lesson,
                        Class_room.class_room,
                        Infos_teacher.tel,
                        Infos_teacher.add,
                        Infos_teacher.email)\
                            .join(Lesson)\
                            .join(Class_room)\
                            .join(Infos_teacher)\

    if name:
        query = query.filter(Teachers.name.like(f'%{name}%'))
    if class_room:
        query = query.filter(Class_room.class_room == class_room)
    if lesson:
        query = query.filter(Lesson.lesson == lesson)
    rows = query.order_by(Class_room.class_room).all()

    keys = ['id', 'name', 'lesson', 'class_room', 'tel', 'add', 'email']
    result = [dict(zip(keys, row)) for row in rows]
    return result

def db_show_lesson():
    data = db.session.query(Lesson.lesson).all()
    key = ['lesson']
    return [dict(zip(key, item)) for item in data]
    
def db_update_info(id, name = None, lesson = None, class_room = None, tel = None, add = None, email = None):
    #lấy thông tin và update
    teacher = Teachers.query.filter(Teachers.id == id).first()
    info = Infos_teacher.query.filter(Infos_teacher.teacher_id == id).first()
    if not teacher or not info:
        return False
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
