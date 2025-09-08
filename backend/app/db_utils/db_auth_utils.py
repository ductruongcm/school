from app.extensions import db
from app.schemas import Users, Info
from app.routes.auth import auth_utils
    
def db_register_gg(username, email, name):
    existing_username = Users.query.filter(Users.username == username).first()
    if existing_username:
        ext = db.session.query(db.func.max(Users.id)).scalar()
        username = f"{username}{ext + 1}"

    password = auth_utils.generate_password(length = 32)
    new_user = Users(username = username, password = password, email = email)
    db.session.add(new_user)
    db.session.flush()
    new_info = Info(user_id = new_user.id, name = name)
    db.session.add(new_info)
    db.session.commit()

def info(username):
    user = Users.query.filter(Users.username == username).first()
    info = Info.query.filter(Info.user_id == user.id).first()
    name = info.name
    email = user.email
    tel = info.tel
    add = info.add
    class_room = info.class_room
    return name, email, tel, add, class_room

def register(username, password, name, email):
    user = Users(username = username, password = password, email = email)
    db.session.add(user)
    db.session.flush()
    info = Info(user_id = user.id, name = name)
    db.session.add(info)
    db.session.commit()

def role(username):
    role = Users.query.filter_by(username = username).first().role
    return role
        

  