from app.schemas import Users, Info
from app.extensions import db

def db_info_update(data, username):
    new_name = data['name'].strip() or None
    new_username = data['username'].strip() or None
    new_email = data['email'].strip() or None
    new_role = data['role'].strip() or None
    new_tel = data['tel'].strip() or None
    new_add = data['add'].strip() or None
    new_class = data['class_room'] or None
    user = Users.query.filter(Users.username == username).first()
    info = Info.query.filter(Info.user_id == user.id).first()
    user.username = new_username if new_username else user.username
    user.email = new_email if new_email else user.email
    user.role = new_role if new_role else user.role
    info.name = new_name if new_name else info.name
    info.tel = new_tel if new_tel else info.tel
    info.add = new_add if new_add else info.add
    info.class_room = new_class if new_class else info.class_room
    db.session.commit()

def db_reset_password(username, new_password):
    user = Users.query.filter_by(username = username).first()
    user.password = new_password
    db.session.commit()