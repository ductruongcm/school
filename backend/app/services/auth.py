from app.utils import set_access_token, set_refresh_token
from app.exceptions import NotFound_Exception
from werkzeug.security import generate_password_hash
from .subservices.sub_auth import Auth_Subservices
from .validation import User_Validation

class AuthService:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.user_repo = self.repo.user
        self.auth_subservices = Auth_Subservices(db, repo)
        self.user_validation = User_Validation(db, repo)

    def handle_login(self, data):    
        user = self.auth_subservices.check_login(data)

        access_token = set_access_token(user)
        refresh_token = set_refresh_token(user)
        
        return {'access_token': access_token, 'refresh_token': refresh_token, 
                'role': user.role, 'id': user.id, 'username': user.username}
    
    def handle_add_user(self, data):      
        #check dup user
        self.user_validation.check_dup_username(data)

        #check xác nhận mật khẩu
        self.user_validation.validate_password(data)
     
        user = self.user_repo.add_user({'username': data['username'],
                                   'password': generate_password_hash(data['password']),
                                   'role': 'admin',
                                   'changed_password': True})
        return user
    
    def get_user_by_id(self, data):
        user = self.user_repo.get_user_by_id(data)
        if not user:
            raise NotFound_Exception('Không tìm thấy ID user!')
        
        return user

    def handle_refresh_token(self, data):
        user = self.get_user_by_id(data)

        access_token = set_access_token(user)
        
        return {'access_token': access_token, 
                'role': user.role, 
                'id': user.id, 
                'username': user.username}
    
    def handle_check_tmp_token(self, data):
        user = self.auth_subservices.check_tmp_token(data)
        return {'id': user.user_id,'username': user.username}

        

    


