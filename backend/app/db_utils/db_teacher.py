from app.schemas.teacher_schemas import Teachers, Infos_teacher, Lesson
from app.schemas.class_room_schemas import Class_room
from app.extensions import db
from sqlalchemy import func


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
    query = Teachers.query.with_entities(Teachers.name,
                        Lesson.lesson,
                        Class_room.class_room,
                        Infos_teacher.tel,
                        Infos_teacher.add,
                        Infos_teacher.email)\
                            .join(Lesson, Teachers.lesson_id == Lesson.id)\
                            .join(Class_room, Teachers.class_room_id == Class_room.id)\
                            .join(Infos_teacher, Teachers.id == Infos_teacher.teacher_id)\

    if name:
        query = query.filter(Teachers.name.like(f'%{name}%'))
    if class_room:
        query = query.filter(Class_room.class_room == class_room)
    if lesson:
        query = query.filter(Lesson.lesson == lesson)
    rows = query.order_by(Class_room.class_room).all()

    keys = ['name', 'lesson', 'class_room', 'tel', 'add', 'email']
    result = [dict(zip(keys, row)) for row in rows]
    return result

def db_show_lesson():
    data = db.session.query(Lesson.lesson).all()
    key = ['lesson']
    return [dict(zip(key, item)) for item in data]
    
# def db_search(current_lesson = None, current_name = None, current_class_room = None):
#     result = Teachers.query
#     if current_lesson:
#         lesson = Lesson.query.filter(Lesson.lesson == current_lesson).first()
#         result.filter(Teachers.lesson_id == lesson.id)
#     if current_name:
#         result.filter(Teachers.name.like(f'%{current_name}%'))
#     if current_class_room:
#         class_room = Class_room.query.filter(Class_room.class_room == current_class_room).first()
#         result.filter(Teachers.class_room_id == class_room.id)
#     return result.all()