import string
import secrets
from datetime import timedelta
from flask_jwt_extended import create_access_token, create_refresh_token

def generate_password(length = 32):
    #Tạo 1 chuỗi chars gồm chữ cái + số + dấu
    #Từ đó bí mật chọn 1 ký tự từ chuỗi đó
    #lặp lại 32 lần và nối lại ta có 1 chuỗi mật mã có 32 ký tự
    chars = string.ascii_letters + string.digits*2 + string.punctuation*2 + string.ascii_uppercase 
    return ''.join(secrets.choice(chars) for _ in range(length))

def token_set_password(length = 32):
    chars = string.ascii_uppercase + string.ascii_uppercase + string.punctuation + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def set_access_token(user):
    return create_access_token(identity = user.username,
                               expires_delta = timedelta(minutes = 15),
                               additional_claims = {'role': user.role, 'id': user.id})

def set_refresh_token(user):
    return create_refresh_token(identity = user.username,
                                expires_delta = timedelta(hours = 10),
                                additional_claims = {'role': user.role, 'id': user.id})
