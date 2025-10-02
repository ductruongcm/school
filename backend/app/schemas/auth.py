from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Annotated
import re

class Register(BaseModel):
    username: Annotated[str, Field(min_length = 8, pattern = r"^[a-z0-9_]+$")]
    password: Annotated[str, Field(min_length = 8)]
    repassword: Annotated[str, Field(min_length = 8)]
    name: str 
    @field_validator('name')
    def name_validator(cls, v):
        if not v:
            raise ValueError('Chưa nhập tên!')
        
        elif not re.fullmatch(r"^[^\W\d_]+(?:\s[^\W\d_]+)*$", v, flags=re.UNICODE):
            raise ValueError("Tên không được chứa số và ký tự đặc biệt!")
        
        return v
 
    @field_validator('password', 'repassword')
    def password_validator(cls, v):
        if not v:
            raise ValueError('Chưa nhập password')
        
        elif not re.search(r'\d', v):
            raise ValueError('Password phải có ít nhất 1 số!')
        
        elif not re.search(r'[A-Z]',v):
            raise ValueError('Password phải có ít nhất 1 chữ in hoa!')
        
        elif not re.search(r'[`~!@#$%^&*()_+=:;.,<>-]',v):
            raise ValueError('Password phải có ít nhất 1 ký tự đặc biệt!')
        
        return v
    
class Login(BaseModel):
    username: str
    password: str

    @field_validator('username')
    def username_validator(cls, v):
        if not v:
            raise ValueError('Chưa nhập tên đăng nhập')
        
        elif not re.match(r'^[a-z0-9_]{8,}$', v):
            raise ValueError('Tên đăng nhập không hợp lệ!')
        
        return v

    @field_validator('password')
    def password_validator(cls, v):
        if not v:
            raise ValueError('Chưa nhập mật khẩu!')
        
        elif not re.fullmatch(r'^(?=.*\d)(?=.*[A-Z])(?=.*[`~!@#$%^&*()_+=:;.,<>-]).{8,}$', v):
            raise ValueError('Mật khẩu không hợp lệ!')
        
        return v

class SetPassword(BaseModel):
    token: str
    password: Annotated[str, Field(min_length = 8)]
    repassword: Annotated[str, Field(min_length = 8)]

    @field_validator('password', 'repassword')
    def password_validator(cls, v):
        if not v:
            raise ValueError('Chưa nhập password')
        
        elif not re.search(r'\d', v):
            raise ValueError('Password phải có ít nhất 1 số!')
        
        elif not re.search(r'[A-Z]',v):
            raise ValueError('Password phải có ít nhất 1 chữ in hoa!')
        
        elif not re.search(r'[`~!@#$%^&*()_+=:;.,<>-]',v):
            raise ValueError('Password phải có ít nhất 1 ký tự đặc biệt!')
        
        return v