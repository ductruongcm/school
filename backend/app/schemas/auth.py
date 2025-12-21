from pydantic import BaseModel, field_validator, EmailStr
import re


class Username(BaseModel):
    username: str
    
    @field_validator('username')
    def username_validator(cls, v):
        if not v:
            raise ValueError('Chưa nhập tên đăng nhập')
        
        elif not re.match(r'^[a-z0-9_]{8,}$', v):
            raise ValueError('Tên đăng nhập không hợp lệ!')
        
        return v

class Password(BaseModel):
    password: str
    repassword: str

    @field_validator('password')
    def password_validator(cls, v):
        if not v:
            raise ValueError('Chưa nhập password')
        
        elif len(v) < 8:
            raise ValueError('Password phải có ít nhất 8 ký tự')

        elif not re.search(r'\d', v):
            raise ValueError('Password phải có ít nhất 1 số!')
        
        elif not re.search(r'[A-Z]',v):
            raise ValueError('Password phải có ít nhất 1 chữ in hoa!')
        
        elif not re.search(r'[`~!@#$%^&*()_+=:;.,<>-]',v):
            raise ValueError('Password phải có ít nhất 1 ký tự đặc biệt!')
        
        return v

class Tmp_token(BaseModel):
    token: str

class Login(Username):
    password: str
    year_id: int

    @field_validator('password')
    def password_validator(cls, v):
        if not v:
            raise ValueError('Chưa nhập mật khẩu!')
        
        elif not re.fullmatch(r'^(?=.*\d)(?=.*[A-Z])(?=.*[`~!@#$%^&*()_+=:;.,<>-]).{8,}$', v):
            raise ValueError('Mật khẩu không hợp lệ!')
        
        return v

class SetPassword(Password):
    token: str
    user_id: int

class Role(BaseModel):
    role: str

    @field_validator('role')
    def validate_role(cls, v):
        if v not in ['admin', 'Teacher', 'Student']:
            raise ValueError('Role không hợp lệ!')
        
        return v

    
