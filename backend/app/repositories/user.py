from app.models import Users, Teacher_info, Teachers, Student_info, Tmp_token, Students
from .base import BaseRepo
from app.extensions import db
from datetime import datetime
import math

class UsersRepo(BaseRepo):
    def get_user(self, data: dict):
        return self.db.session.query(Users).filter(Users.username == data['username']).first()
    
    def get_user_by_id(self, data: dict):
        return self.db.session.query(Users).filter(Users.id == data['user_id']).first()
    
    def get_user_by_tmp_token(self, data: dict):
        return self.db.session.query(Tmp_token.user_id,
                                     Users.username).join(Users).filter(Tmp_token.token == data['token'], 
                                                                        Tmp_token.expire_at > datetime.utcnow(), 
                                                                        Tmp_token.set_password_status == False).first()
       
    def get_tmp_token_by_user_id(self, data: dict):
        return self.db.session.query(Tmp_token).filter(Tmp_token.user_id == data['user_id']).first()
    
    def get_user_info(self, data: dict):
        if data['role'] in ['Teacher', 'admin']:
            return self.db.session.query(Users.username,
                                        Teachers.name,
                                        Teacher_info.email,
                                        Teacher_info.tel,
                                        Teacher_info.add).join(Users.teachers).outerjoin(Teachers.teacher_info).filter(Users.id == data['user_id']).first()
            
        return self.db.session.query(Users.username,
                                    Students.name,
                                    Student_info.tel,
                                    Student_info.add).join(Students).outerjoin(Student_info).filter(Users.id == data['user_id']).first()
     
    def add_user(self, data: dict):
        new_user = Users(username = data['username'], password = data['hashed_password'], role = 'admin')
        new_user.teachers = [Teachers(name = data['name'])]
        self.db.session.add(new_user)

    def set_password(self, data: dict):
        self.db.session.query(Users).filter(Users.id == data['user_id']).update({Users.password: data['password']})
        self.db.session.query(Tmp_token).filter(Tmp_token.user_id == data['user_id']).update({Tmp_token.set_password_status: True})

    def show_user(self, data: dict):
        username = data['username']
        role = data['role']
        page = data['page']

        query = self.db.session.query(Users.id, Users.username, Users.role)

        if username:
            query = query.filter(Users.username.ilike(f'%{username}%'))
        if role:
            query = query.filter(Users.role.ilike(f'%{role}%'))

        all_records = query.count()
        limit = 25
        total_pages = math.ceil(all_records/limit) if all_records > limit else 1
        offset = (page - 1) * limit 

        query = query.order_by(Users.username).limit(limit).offset(offset).all()

        keys = ['id', 'username', 'role']
        data = [dict(zip(keys, values)) for values in query]
        return {'data': data, 'total_pages': total_pages, 'page': page}
    
    def show_teacher_info(self, data: dict):
            return self.db.session.query(Teachers.name,
                                        Teacher_info.email,
                                        Teacher_info.tel,
                                        Teacher_info.add).outerjoin(Teacher_info).filter(Teachers.user_id == data['id']).first()
    
    def show_student_info(self, data: dict):
        return self.db.sesson.query(Students.name,
                                    Student_info.tel,
                                    Student_info.add).join(Student_info).filter(Students.user_id == data['id']).first()
        
        

        



        
        



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

def db_update_role(username, role):
    user = Users.query.filter(Users.username == username).first()
    user.role = role
    db.session.commit()

    