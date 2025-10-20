from app.utils import set_access_token, set_refresh_token
from app.exceptions import CustomException
from app.validators import Validation_helpers
from werkzeug.security import generate_password_hash
from .base import BaseService
from .subservices.sub_auth import AuthSub_service

class AuthService(BaseService):
    def __init__(self, db, repo):
        super().__init__(db)
        self.repo = repo(db)

    def handle_login(self, data):    
        user = AuthSub_service(self.repo).check_user(data)

        access_token = set_access_token(data, user)
        refresh_token = set_refresh_token(data, user)
        
        return {'status': 'Success', 
                'access_token': access_token, 'refresh_token': refresh_token, 
                'role': user.role, 'id': user.id, 'username': user.username}
    
    def handle_register(self, data):        
        if self.repo.get_user(data): 
            raise CustomException('Username đã được sử dụng!')

        elif logic_error:= Validation_helpers.password_validation(data['password'], data['repassword']): 
            raise CustomException(logic_error) 

        else:
            data['hashed_password'] = generate_password_hash(data['password'])
            self.repo.add_user(data)
            self.db.session.commit()
            return {'status': 'Success', 'username': data['username']}
        
    def handle_refresh_token(self, data):
        user = self.repo.get_user(data)
        if not user: 
            raise CustomException('User không tồn tại!')

        access_token = set_access_token(data, user)
        
        return {'status': 'Success', 
                'access_token': access_token, 
                'role': user.role, 
                'id': user.id, 
                'username': user.username}

    


