import re

class Validation_helpers:   
    @staticmethod
    def password_validation(v, re_v):
        errors = {'field': 'Password'}
        if not v:
            errors['msg'] = 'Chưa nhập mật khẩu!'
        elif v != re_v:
            errors['msg'] = 'Xác nhận mật khẩu không khớp!'
        return errors if 'msg' in errors else None
    
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
    
class Password_helpers:
    def __init__(self):
        self.validator = Validation_helpers
        
    def validate(self, password, repassword):
        errors = []
        if self.validator.password_validation(password, repassword):
            errors.append(self.validator.password_validation(password, repassword))

        return errors 
    





