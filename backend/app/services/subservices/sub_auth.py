from werkzeug.security import check_password_hash
from app.validators import Validation_helpers
from app.exceptions import NotFound_Exception, CustomException

class Auth_Subservices:
    def __init__(self, db, repo):
        self.repo = repo(db)
        self.user_repo = self.repo.user

    def check_login(self, data):   
        user = self.user_repo.get_user_by_username(data)
        if not user:
            raise NotFound_Exception('Username hoặc mật khẩu không đúng!')
        
        elif not check_password_hash(user.password, data.get('password')):
            raise NotFound_Exception('Username hoặc mật khẩu không đúng!')
        
        return user

    def check_tmp_token(self, data):
        user  = self.user_repo.get_user_by_tmp_token(data)
        if not user:
            raise NotFound_Exception('Không tìm thấy User ID!')
        return user
          
    def check_password(self, data):
        if errors:= Validation_helpers.password_validation(data['password'], data['repassword']):
            raise CustomException(errors)

