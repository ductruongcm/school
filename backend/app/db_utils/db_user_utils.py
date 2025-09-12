from app.schemas import Users, Info
from app.extensions import db

def db_info_update(id, new_name = None, new_role = None, new_username = None, new_email = None, new_tel = None, new_add = None):
    user = Users.query.filter(Users.id == id).first()
    info = Info.query.filter(Info.user_id == id).first()
    if new_name:
        info.name = new_name
    if new_role:
        user.role = new_role
    if new_username:
        user.username = new_username
    if new_email:
        user.email = new_email
    if new_tel:
        info.tel = new_tel
    if new_add:
        info.add = new_add
    db.session.commit()

def db_reset_password(username, new_password):
    user = Users.query.filter_by(username = username).first()
    user.password = new_password
    db.session.commit()