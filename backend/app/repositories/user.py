from app.models import Users, Tmp_token
from app.extensions import db
from datetime import datetime
import math

class UserRepo:
    def __init__(self, db):
        self.db = db

    def insert_user(self, data: dict):
        new_user = Users(**data)
        self.db.session.add(new_user)
        self.db.session.flush()
        return new_user
    
    def insert_tmp_token(self, data: dict):
        #user_id, tmp_token
        self.db.session.add(Tmp_token(**data))

    def get_user_by_username(self, data: dict):
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
    
def db_update_role(username, role):
    user = Users.query.filter(Users.username == username).first()
    user.role = role
    db.session.commit()

    