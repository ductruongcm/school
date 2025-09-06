from app.extensions import db
from app.routes.user.user_schemas import Users, Info
import string
import secrets

def generate_password(length = 32):
    #Tạo 1 chuỗi chars gồm chữ cái + số + dấu
    #Từ đó bí mật chọn 1 ký tự từ chuỗi đó
    #lặp lại 32 lần và nối lại ta có 1 chuỗi mật mã có 32 ký tự
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(chars) for _ in range(length))
    
def register_gg(username, email, name):
    existing_username = Users.query.filter(Users.username == username).first()
    if existing_username:
        ext = db.session.query(db.func.max(Users.id)).scalar()
        username = f"{username}{ext + 1}"

    password = generate_password(length = 32)
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
        

  