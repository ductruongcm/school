from app.extensions import db
from app.schemas import Students, Class_room, Users, Info
from app.routes.auth.auth_utils import generate_password
from werkzeug.security import generate_password_hash

def generate_student_id(year, current_class_room):
    year_id = year[2:4:1]
    class_id = Class_room.query.filter(Class_room.class_room == current_class_room).first().id
    if class_id < 10:
        student_id = f'{year_id}0{class_id}00'
    else:
        student_id = f'{year_id}{class_id}00'
    return student_id

def db_add_student(name, current_class_room, tel, add, role, year):
    class_room = Class_room.query.filter(Class_room.class_room == current_class_room).first()
    new_student = Students(name = name, class_room_id = class_room.id)
    db.session.add(new_student)
    db.session.flush()
    username = generate_student_id(year, current_class_room) 
    if new_student.id < 10:
        username = f'{username}0{new_student.id}'
    else:
        username = f'{username}{new_student.id}'
    password = generate_password_hash(generate_password(length = 32))
    new_student.student_id = username
    new_user = Users(username = username, password = password, role = role)
    new_info = Info(user_id = new_user.id, name = name, tel = tel, add = add)
    db.session.add_all([new_user, new_info])
    db.session.flush()
    new_student.info_id = new_info.id
    db.session.commit()

def db_show_student(current_class_room):
    class_room = Class_room.query.filter(Class_room.class_room == current_class_room).first()
    
    rows = db.session.query(Students.name, 
                           Info.tel, 
                           Info.add).join(Students, Students.info_id == Info.id).filter(Students.class_room_id == class_room.id).all()
    keys = ['name', 'tel', 'add']
    return [dict(zip(keys, row)) for row in rows]
    

   