import re
from app.schemas import Users, Class_room, Year
from werkzeug.security import check_password_hash

def username_validates(username = None):
    errors = []
    user = Users.query.filter_by(username = username).first()
    if username:
        if user:
            errors.append('Username đã có người dùng, vui lòng đổi username khác')
        if len(username) < 8:
            errors.append('Username phải có ít nhất 8 ký tự')
        if not re.fullmatch(r'[a-z0-9_]{8,}', username):
            errors.append('Username không được chứa ký tự đặc biệt')
    return errors

def password_validates(password = None,
                       repassword = None):
    errors = []
    if password:
        if password != repassword:
            errors.append('Xác nhận mật khẩu không chính xác')
        if len(password) < 8:
            errors.append('Password phải có ít nhất 8 ký tự')
        if not re.fullmatch(r'(?=.*\d)(?=.*[A-Z])(?=.*[!@#$%^&*<>,.;:-_=]).*', password):
            errors.append('Password phải chứa 1 ký tự đặc biệt, 1 số và 1 chữ in hoa')
    return errors

def name_validates(name = None):
    errors = []
    if name:
        if name == None:
            errors.append('Chưa nhập tên!')
        if not re.fullmatch(r'[A-Za-zÀ-ỹ\s]+', name):              
            errors.append('Tên không được chứa số và ký tự đặc biệt')
    return errors

def class_validates(current_class_room = None, current_year = None):
    errors = []
    if current_year and current_class_room:
        year = Year.query.filter(Year.year == current_year).first() 
        class_room = Class_room.query.filter(Class_room.class_room == current_class_room, year.id == Class_room.year_id).first()
        if not year:
            errors.append('Niên khóa không đúng!')
        if not class_room:
            errors.append('Thông tin lớp học không đúng!!')
    return errors
    
def email_validates(email = None):
    errors = []
    if email:
        if re.search(r'[-!#$%^&*=,<>]+', email):
            errors.append('Email không hợp lệ!')
        if Users.query.filter_by(email = email).first():
            errors.append('Email này đã được sử dụng, hãy vào quên mật khẩu để lấy lại mật khẩu')
    return errors

def tel_validates(tel = None):  
    errors = []
    if tel:
        if not re.fullmatch(r'\d{10}', tel):
            errors.append('Số điện thoại chỉ được chứa 10 số!')
    return errors

def add_validates(add = None):
    errors = []
    if add:
        if re.search('[!@#$%^&*(_+=,.<>?)]', add):
            errors.append('Địa chỉ không được chứa ký tự đặc biệt!')
    return errors

def errors(username = None, password = None, repassword = None, name = None, tel = None, email = None, add = None, class_room = None, year = None):
    errors = []
    errors.extend(username_validates(username) or []) 
    errors.extend(password_validates(password, repassword) or []) 
    errors.extend(name_validates(name) or []) 
    errors.extend(tel_validates(tel) or [])
    errors.extend(email_validates(email) or []) 
    errors.extend(add_validates(add) or [])
    errors.extend(class_validates(class_room, year) or [])
    return errors

def login_validates(username, password):
    user = Users.query.filter_by(username = username).first()

    if not user:
        error = "Username không tồn tại"
        return error
    if not check_password_hash(user.password, password):
        error = 'Sai mật khẩu!!'
        return error
    
