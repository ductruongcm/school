from app.schemas.teacher_schemas import Teachers, Infos_teacher, Lesson, Teach_room
from app.schemas.class_room_schemas import Class_room
from app.extensions import db
from sqlalchemy import func, cast, literal, Text, literal_column, text
from sqlalchemy.orm import aliased

def db_add_lesson(lesson):
    new_lesson = Lesson(lesson = lesson)
    db.session.add(new_lesson)
    db.session.commit()

def db_add_teacher(name, current_lesson, current_teach_room, tel, add, email, current_class_room = None):
    lesson = Lesson.query.filter(Lesson.lesson == current_lesson).first()
    teach_cls = Class_room.query.filter(Class_room.class_room == current_teach_room).first()

    if current_class_room:
        class_room = Class_room.query.filter(Class_room.class_room == current_class_room).first()
        new_teacher = Teachers(name = name, lesson_id = lesson.id, class_room_id = class_room.id)
    else:
        new_teacher = Teachers(name = name, lesson_id = lesson.id)    
    db.session.add(new_teacher)
    db.session.flush()
    new_teacher_info = Infos_teacher(teacher_id = new_teacher.id, email = email, tel = tel, add = add)
    new_teach_room = Teach_room(teacher_id = new_teacher.id, teach_room = teach_cls.id)
    db.session.add_all([new_teacher_info, new_teach_room])
    db.session.commit()

def db_show_teacher(lesson = None, class_room = None, name = None):
    #Show table bằng join các tables đồng thời search
    #Chỉ join, không chốt table để search

    Teachclass = aliased(Class_room)
    teach_room_expr = text(
        "coalesce(string_agg(class_room_1.class_room, ', ' ORDER BY class_room_1.class_room), '') AS teach_room"
    )
    #đoạn trên phải viết raw SQL vì lý do dấu phấy khi nhúng vào postgre gây hiểu lầm => ở filter cũng phải raw SQL mới đc ko thể dùng like/ilike
    query = Teachers.query.with_entities(Teachers.id,
                        Teachers.name,
                        Lesson.lesson,
                        Class_room.class_room,
                        teach_room_expr,
                        Infos_teacher.tel,
                        Infos_teacher.add,
                        Infos_teacher.email)\
                            .join(Lesson)\
                            .outerjoin(Class_room, Class_room.id == Teachers.class_room_id)\
                            .outerjoin(Teach_room, Teach_room.teacher_id == Teachers.id)\
                            .outerjoin(Teachclass, Teachclass.id == Teach_room.teach_room)\
                            .join(Infos_teacher)\
                            .group_by(
                                Teachers.id,
                                Teachers.name,
                                Lesson.lesson,
                                Class_room.class_room,
                                Infos_teacher.tel,
                                Infos_teacher.add,
                                Infos_teacher.email
                            )

    if name:
        query = query.filter(Teachers.name.like(f'%{name}%'))
    if lesson:
        query = query.filter(Lesson.lesson == lesson)
    if class_room:
        query = query.having(text("string_agg(class_room_1.class_room, ', ' ORDER BY class_room_1.class_room) LIKE :val")).params(val=f'%{class_room}%')
    rows = query.order_by(Class_room.class_room).all()

    keys = ['id', 'name', 'lesson', 'class_room', 'teach_room', 'tel', 'add', 'email']
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

def db_update_teach_room(id, teach_room = None):
    if teach_room:
        #Lấy tất cả teach_room hiện tại sao với tất cả teach_room mới
        #So sanh list cũ và list mới, cái nào dư ra so với list cũ thì add, cái này thiếu đi thì xóa

        teach_room_list = [cls.strip() for cls in teach_room.split(',')]
        #chuyển teach_room về list để duyệt in
        current_class = {row.teach_room for row in Teach_room.query.filter(Teach_room.teacher_id == id).all()}
        new_class = {cls.id for cls in Class_room.query.filter(Class_room.class_room.in_(teach_room_list)).all()}

        #Sau khi có đc 2 set, sẽ add và delete
        to_add = new_class - current_class
        to_delete = current_class - new_class

        if to_add:    
            db.session.add_all([
                Teach_room(teacher_id = id, teach_room = cls_add) for cls_add in to_add
            ])
        
        if to_delete:
            Teach_room.query.filter(Teach_room.teacher_id == id, Teach_room.teach_room.in_(to_delete)).delete(synchronize_session=False)
        db.session.commit()    