from app.schemas import Users, Info, Infos_teacher, Teachers
from app.extensions import db
from werkzeug.security import generate_password_hash

def db_info_update(id, new_name, new_role, new_username, new_email = None, new_tel = None, new_add = None):
    user = Users.query.filter(Users.id == id).first()
    
    if new_role == 'teacher':
        info = Infos_teacher.query.filter(Infos_teacher.user_id == id).first()
    else:
        info = Info.query.filter(Info.user_id == id).first()
    
        if new_name != info.name :
            info.name = new_name
        if new_username != user.username:
            user.username = new_username
        if new_email != info.email:
            info.email = new_email
        if new_tel != info.tel:
            info.tel = new_tel
        if new_add != info.add:
            info.add = new_add
            
    db.session.commit()

def db_reset_password(username, new_password):
    user = Users.query.filter_by(username = username).first()
    user.password = new_password
    db.session.commit()

def db_show_users(username = None, role = None):
    query = db.session.query(Users.username, Users.role)
    if username:
        query = query.filter(Users.username.ilike(f'%{username}%'))
    if role:
        query = query.filter(Users.role.ilike(f'%{role}%'))
    rows = query.order_by(Users.username).all()
    keys = ['username', 'role']
    return [dict(zip(keys, row)) for row in rows]

def db_update_role(username, role):
    user = Users.query.filter(Users.username == username).first()
    user.role = role
    db.session.commit()

def db_set_password(username, password):
    user = Users.query.filter(Users.username == username).first()
    hash_password = generate_password_hash(password)
    user.password = hash_password
    db.session.commit()

def info(id, role):
    if role == 'teacher':
        info = Infos_teacher.query.filter(Infos_teacher.user_id == id).first()
        name = Teachers.query.filter(Teachers.user_id == id).first().name
    else:
        info = Info.query.filter(Info.user_id == id).first()
        name = info.name
    email = info.email
    tel = info.tel
    add = info.add
    
    return {'name': name, 'tel': tel, 'add': add, 'email': email}