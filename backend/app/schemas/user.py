from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Annotated, Optional
import re

class UserSchemas:
    class User(BaseModel):
        name: str
        lesson: str
        class_room: Optional[str] = None
        tel: str
        add: str
        username: str
        email: EmailStr
        role: str
        year: Annotated[str, Field(len = 11, pattern = r"^[0-9- ]+$")]

        @field_validator('username')
        def username_validator(cls, v):
            if not re.match(r'^[a-z0-9_]{8,}$', v):
                raise ValueError('Tên đăng nhập không hợp lệ!')
            return v
        
        @field_validator('name', 'lesson')
        def name_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập thông tin tên hoặc môn học!')
            
            if re.search(r"[\d~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Thông tin không được chứa số và ký tự đặc biệt!")
            return v

        @field_validator('class_room')
        def class_validator(cls, v):
            if not v:
                return
            elif len(v) != 3:
                raise ValueError('Tên lớp chỉ có 3 ký tự!')
            elif not re.fullmatch(r'[\dA-Z]+', v):
                raise ValueError('Tên lớp chỉ chứa số và chữ in hoa!')
            return v
        
        @field_validator('tel')
        def tel_validator(cls, v):
            if not re.fullmatch(r'\d{10}', v):
                raise ValueError('Số điện thoại chỉ được chứa 10 chữ số')
            return v
        
        @field_validator('add')
        def str_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập thông tin địa chỉ!')
            
            if re.search(r"[~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Thông tin không được chứa số và ký tự đặc biệt!")
            return v

    class UserShowSchema(BaseModel):
        username: Optional[str] = None
        role: Optional[str] = None
        page: Optional[int]

        @field_validator('username')
        def username_validator(cls, v):
            if not v:
                return
            elif not re.match(r'^[a-z0-9_]{8,}$', v):
                raise ValueError('Username không hợp lệ!')
            return v
        
        @field_validator('role')
        def role_validator(cls, v):
            if not v:
                return
            elif not re.match(r'^[a-z]{8,}$', v):
                raise ValueError('Role không hợp lệ!')
            return v

    class UserInfoUpdateSchema(BaseModel):
        id: int
        name: str
        username: str
        email: EmailStr
        tel: str
        add: str

        @field_validator('username')
        def username_validator(cls, v):
            if not re.match(r'^[a-z0-9_]{8,}$', v):
                raise ValueError('Tên đăng nhập không hợp lệ!')
            return v
        
        @field_validator('name', 'add')
        def name_validator(cls, v):
            if re.search(r"[\d~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Tên/địa chỉ không được chứa số và ký tự đặc biệt!")
            return v
        
        @field_validator('tel')
        def tel_validator(cls, v):
            if not re.fullmatch(r'\d{10}', v):
                raise ValueError('Số điện thoại chỉ được chứa 10 chữ số')
            return v
    
class Student(UserSchemas.User):
    score_oral: float
    score_15m: float
    score_45m: float
    score_final: float
    total: float
    remark: str
    rank: str

    @field_validator('remark', 'rank')
    def str_validator(cls, v):
        if re.search(r'[`~!@#$%^&*(=+,<>/?_-)]', v):
            raise ValueError('Khu vực không được chứa ký tự đặc biệt')
        return v
    
class TeacherSchemas:    
    class TeacherCreateSchema(UserSchemas.User):
        teach_room: list

    class TeacherShowSchema(BaseModel):
        name: Optional[str] = None
        lesson: Optional[str] = None
        class_room: Optional[str] = None

        @field_validator('name', 'lesson')
        def name_validator(cls, v):
            if not v:
                return 
            if re.search(r"[\d~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Thông tin tên không chứa số và ký tự đặc biệt!")
            return v
        
        @field_validator('class_room')
        def class_validator(cls, v):
            if not v:
                return 
            if len(v) > 3:
                raise ValueError('Tên lớp chỉ có 3 ký tự. VD: 10A')
            if not re.fullmatch(r'[\dA-Za-z]+', v):
                raise ValueError('Thông tin Tên lớp không chứa ký tự đặc biệt. VD: 10A')
            return v
        
        @field_validator('lesson')
        def lesson_validator(cls, v):
            if not v:
                return 
            
            if re.search(r"[\d~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Thông tin môn học không chứa số và ký tự đặc biệt!")
            return v

    class TeacherUpdateSchema(BaseModel):
        id: int
        name: str
        lesson: str
        class_room: Optional[str] = None
        teach_room: str
        tel: str
        add: str
        email: EmailStr
        year: Annotated[str, Field(len = 11, pattern = r"^[0-9- ]+$")]

        @field_validator('name', 'lesson')
        def name_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập thông tin tên hoặc môn học!')
            
            elif re.search(r"[\d~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Thông tin không được chứa số và ký tự đặc biệt!")
            return v

        @field_validator('tel')
        def tel_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập thông tin số điện thoại!')
            elif not re.fullmatch(r'\d{10}', v):
                raise ValueError('Số điện thoại chỉ được chứa 10 chữ số!')
            return v
        
        @field_validator('class_room')
        def class_validator(cls, v):
            if not v:
                return
            elif len(v) != 3:
                raise ValueError('Tên lớp không đúng. VD: 10A')
            elif not re.fullmatch(r'[\dA-Z]+', v):
                raise ValueError('Tên lớp chỉ chứa số và chữ in hoa!')
            return v
        
        @field_validator('teach_room')
        def class_room_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập thông tin lớp giảng dạy!')
            
            elif not re.fullmatch(r'[\dA-Z, -]+', v):
                raise ValueError('Tên lớp chỉ chứa số và chữ in hoa. VD: 10A - 10B')
            return v
        
        @field_validator('add')
        def add_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập thông tin địa chỉ!')
            
            elif re.search(r"[~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Thông tin không được chứa số và ký tự đặc biệt!")
            return v