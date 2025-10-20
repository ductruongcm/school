import re
from werkzeug.security import check_password_hash

class Validation_helpers:  
    def __init__(self, repo):
        self.repo = repo
    
    def existing_user(self, data: dict):
        user = self.repo.get_user(data)
        if not user or not check_password_hash(user.password, data['password']):
            raise ValueError('Sai tên đăng nhập hoặc không đúng mật khẩu!')
        return user

    @staticmethod
    def password_validation(v, re_v):
        if v != re_v:
            raise ValueError('Xác nhận mật khấu không đúng')
      
    @staticmethod
    def score_validation(v: float):
        errors = {'field': 'Điểm số'}
        if not re.fullmatch(r'[\d.]*', v):
            errors['msg'] = 'Điểm số chỉ được chứa chữ số'
        else:
            if v < 0:
                errors['msg'] = 'Điểm số không được nhỏ hơn 0!'
            elif v > 10:
                errors['msg'] = 'Điểm số không được lớn hơn 10!'
        return errors if 'msg' in errors else None 
    
    @staticmethod
    def filename_validation(v):
        errors = {'field': 'Filename'}
        if not v:
            errors['msg'] = 'Chưa nhập tên file!'
        elif not re.fullmatch(r'[\da-z_]*', v):
            errors['msg'] = 'tên file chỉ được chứa chữ cái và số. VD: thoi_khoa_bieu'
        return errors if 'msg' in errors else None
    
    





