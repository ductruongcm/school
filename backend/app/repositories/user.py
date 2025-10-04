from app.models import Users, Teacher_info, Teachers, Student_info, Tmp_token, Students
from app.extensions import db
from werkzeug.security import generate_password_hash
from datetime import datetime
import math

# def db_info_update(id, new_name, new_role, new_username, new_email = None, new_tel = None, new_add = None):
#     user = Users.query.filter(Users.id == id).first()
    
#     if new_role == 'teacher':
#         info = Teacher_info.query.filter(Teacher_info.user_id == id).first()
#     else:
#         info = Info.query.filter(Info.user_id == id).first()
    
#         if new_name != info.name :
#             info.name = new_name
#         if new_username != user.username:
#             user.username = new_username
#         if new_email != info.email:
#             info.email = new_email
#         if new_tel != info.tel:
#             info.tel = new_tel
#         if new_add != info.add:
#             info.add = new_add
            
    # db.session.commit()

def db_reset_password(username, new_password):
    user = Users.query.filter_by(username = username).first()
    user.password = new_password
    db.session.commit()

def db_update_role(username, role):
    user = Users.query.filter(Users.username == username).first()
    user.role = role
    db.session.commit()

# def db_set_password(username, password):
#     user = Users.query.filter(Users.username == username).first()
#     hash_password = generate_password_hash(password)
#     user.password = hash_password
#     db.session.commit()

def info(id, role):
    if role == 'teacher':
        info = Teacher_info.query.filter(Teacher_info.user_id == id).first()
        name = Teachers.query.filter(Teachers.user_id == id).first().name
    else:
        info = Student_info.query.filter(Student_info.user_id == id).first()
        name = info.name
    email = info.email
    tel = info.tel
    add = info.add
    
    return {'name': name, 'tel': tel, 'add': add, 'email': email}

class UsersRepositories:
    @staticmethod
    def get_user(username):
        return Users.query.filter(Users.username == username).first()
    
    @staticmethod
    def get_tmp_token(token):
        result = Tmp_token.query.filter(Tmp_token.token == token, 
                                       Tmp_token.expire_at > datetime.utcnow(), 
                                       Tmp_token.status == False).first()
        return result
             
    @staticmethod
    def get_tmp_token_by_id(id):
        return Tmp_token.query.filter(Tmp_token.user_id == id).first()
    
    @staticmethod
    def get_user_info(id, role):
        if role in ['teacher', 'admin']:
            user = Users.query.with_entities(Users.username,
                                         Teachers.name,
                                         Teacher_info.email,
                                         Teacher_info.tel,
                                         Teacher_info.add).join(Teachers).outerjoin(Teacher_info).filter(Users.id == id).first()
            
        user = Users.query.with_entities(Users.username,
                                         Students.name,
                                         Student_info.tel,
                                         Student_info.add).join(Students).outerjoin(Student_info).filter(Users.id == id).first()
        
        return user
     
    @staticmethod
    def add_user(username, password, name):
        new_user = Users(username = username, password = password, role = 'admin')
        new_user.teachers = [Teachers(name = name)]
        db.session.add(new_user)

    @staticmethod
    def set_password(user_id, password):
        Users.query.filter(Users.id == user_id).update({Users.password: password})
        Tmp_token.query.filter(Tmp_token.user_id == user_id).update({Tmp_token.set_password_status: True})

    @staticmethod
    def show_user(username, role, page):
        query = db.session.query(Users.username, Users.role)

        if username:
            query = query.filter(Users.username.ilike(f'%{username}%'))
        
        if role:
            query = query.filter(Users.role.ilike(f'%{role}%'))

        all_records = query.count()
        limit = 25
        total_pages = math.ceil(all_records/limit) if all_records > limit else 1
        offset = (page - 1) * limit 

        query = query.order_by(Users.username).limit(limit).offset(offset).all()

        keys = ['username', 'role']
        data = [dict(zip(keys, values)) for values in query]

        return {'data': data, 'total_pages': total_pages, 'page': page}
    
    @staticmethod
    def show_user_info(id, role):
        if role in ['teacher', 'admin']:
            return [db.session.query(
                            Teachers.name,
                            Teacher_info.email,
                            Teacher_info.tel,
                            Teacher_info.add).outerjoin(Teacher_info).filter(Teachers.user_id == id).first()]



        
        



    