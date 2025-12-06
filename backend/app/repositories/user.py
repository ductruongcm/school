from app.models import Users, Tmp_token, Teachers, Students
from datetime import datetime, timedelta
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import text
import math

class UserRepo:
    def __init__(self, db):
        self.db = db

    def insert_user(self, data: dict):
        new_user = Users(**data)
        self.db.session.add(new_user)
        self.db.session.flush()
        return new_user
    
    def upsert_tmp_token(self, data: dict):
        #user_id, tmp_token
        stmt = insert(Tmp_token).values(**data)
        stmt = stmt.on_conflict_do_update(index_elements= [Tmp_token.user_id],
                                          set_ = {Tmp_token.token: stmt.excluded.token,
                                                  Tmp_token.expire_at: timedelta(hours=7) + datetime.utcnow(),
                                                  Tmp_token.set_password_status: False},
                                          where = text('excluded.token IS DISTINCT FROM tmp_token.token'))
        self.db.session.execute(stmt)

    def get_user_by_username(self, data: dict):
        return self.db.session.query(Users).filter(Users.username == data['username']).first()
    
    def get_user_by_id(self, data: dict):
        return self.db.session.query(Users).filter(Users.id == data['user_id']).first()
    
    def get_user_by_tmp_token(self, data: dict):
        return self.db.session.query(Tmp_token.user_id,
                                     Users.username).join(Users.tmp_token).filter(Tmp_token.token == data['token'],
                                                                                  Tmp_token.set_password_status == False,
                                                                                  Tmp_token.expire_at > datetime.utcnow()).first()
       
    def get_tmp_token_by_user_id(self, data: dict):
        return self.db.session.query(Tmp_token).filter(Tmp_token.user_id == data['user_id']).first()

    def set_password(self, data: dict):
        self.db.session.query(Users).filter(Users.id == data['user_id']).update({Users.password: data['password']})
        self.db.session.query(Tmp_token).filter(Tmp_token.user_id == data['user_id']).update({Tmp_token.set_password_status: True})

    def show_user(self, data: dict):
        username = data['username']
        role = data['role']
        page = data['page']

        query = self.db.session.query(Users.id, Users.username, Users.role, Teachers.name, Students.name).outerjoin(Users.teachers).outerjoin(Users.students)

        if username:
            query = query.filter(Users.username.ilike(f'%{username}%'))
        if role:
            query = query.filter(Users.role.ilike(f'%{role}%'))

        all_records = query.count()
        limit = 25
        total_pages = math.ceil(all_records/limit) if all_records > limit else 1
        offset = (page - 1) * limit 

        query = query.order_by(Users.username).limit(limit).offset(offset).all()

        keys = ['id', 'username', 'role', 'teacher_name', 'student_name']
        data = [dict(zip(keys, values)) for values in query]
        return {'data': data, 'total_pages': total_pages, 'page': page}
    



    