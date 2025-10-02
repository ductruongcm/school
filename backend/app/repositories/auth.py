# from app.extensions import db
# from app.models import Users, Info
# from app.utils import generate_password
    
# def db_register_gg(username, email, name):
#     existing_username = Users.query.filter(Users.username == username).first()
#     if existing_username:
#         ext = db.session.query(db.func.max(Users.id)).scalar()
#         username = f"{username}{ext + 1}"

#     password = generate_password(length = 32)
#     new_user = Users(username = username, password = password, email = email)
#     db.session.add(new_user)
#     db.session.flush()
#     new_info = Info(user_id = new_user.id, name = name)
#     db.session.add(new_info)
#     db.session.commit()
        

    