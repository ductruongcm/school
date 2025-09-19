from app.extensions import db
from app.schemas import Users, Info, Infos_teacher
from app.utils import auth_utils
    
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

def register(username, password, name, email):
    user = Users(username = username, password = password, email = email)
    db.session.add(user)
    db.session.flush()
    info = Info(user_id = user.id, name = name)
    db.session.add(info)
    db.session.commit()

def role(username):
    user = Users.query.filter_by(username = username).first()
    role = user.role
    id = user.id
    return role, id
        

  