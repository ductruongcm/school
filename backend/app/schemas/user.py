from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import date
import re

class UserSchemas:
    class User(BaseModel):
        name: str
        add: str
        
        @field_validator('name')
        def name_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập họ và tên!')
            
            if re.search(r"[\d~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Thông tin không được chứa số và ký tự đặc biệt!")
            return v
        
        @field_validator('add')
        def str_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập thông tin địa chỉ!')
            
            if re.search(r"[~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Thông tin không được chứa ký tự đặc biệt!")
            return v
        
    class UserShowSchema(BaseModel):
        username: Optional[str] = None
        role: Optional[str] = None
        page: Optional[int]

        @field_validator('username')
        def username_validator(cls, v):
            if not v:
                return
            if not re.match(r'^[a-z0-9_]+$', v):
                raise ValueError('Tên đăng nhập không hợp lệ!')
            return v
        
        @field_validator('role')
        def role_validator(cls, v):
            if not v:
                return
            elif not re.match(r'^[A-Za-z]+$', v):
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
    
class StudentSchemas:
        class StudentCreate(UserSchemas.User):
            class_room_id: int | None
            class_room: str | None
            tel: Optional[str] | None
            gender: str
            bod: Optional[date] | None
            year_id: int
            year: str
            grade_id: int
            
            @field_validator('grade_id', mode='before')
            def class_validator(cls, v):
                if v in ['', 'None', 'null']:
                    raise ValueError('Chưa nhập thông tin khối lớp!')
                return v
            
            @field_validator('bod', 'class_room_id', mode='before')
            def bod_validator(cls, v):
                if v in ['', 'None']:
                    return None
                
                return v
        
        class StudentShow(BaseModel):
            grade_id: Optional[int] | None

            @field_validator('grade_id', mode='before')
            def grade_id_validator(cls, v):
                if v in ['', 'None', 'null']:
                    return 
                return v
    
class TeacherSchemas:    
    class TeacherCreateSchema(UserSchemas.User):
        username: str
        tel: str
        teach_class: list
        class_room: Optional[str] | None
        class_room_id: Optional[int] | None
        email: EmailStr
        lesson_id: int
        lesson: str
        year_id: int

        @field_validator('lesson')
        def name_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập họ và tên!')
            
            if re.search(r"[\d~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Thông tin không được chứa số và ký tự đặc biệt!")
            return v

        @field_validator('class_room_id', mode='before')
        def class_room_validation(cls, v):
            if v in ['', 'null', 'None']:
                return None
            return v
                       
        @field_validator('lesson_id', mode='before')
        def lesson_validation(cls, v):
            if v in ['', None]:
                raise ValueError('Chưa nhập thông tin môn học!')
            return v
        
        @field_validator('year_id')
        def year_id_validation(cls, v):
            if v in ['', None]:
                raise ValueError('Hệ thống chưa set niên khóa!')
            return v
        
        @field_validator('tel')
        def tel_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập số điện thoại!')
            elif not re.fullmatch(r'\d{10}', v):
                raise ValueError('Số điện thoại chỉ được chứa 10 chữ số')
            return v
        
        @field_validator('username')
        def username_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập username!')
            elif not re.match(r'^[a-z0-9_]{8,}$', v):
                raise ValueError('Tên đăng nhập không hợp lệ!')
            return v
        
        @field_validator('teach_class')
        def teach_room_validation(cls, v):
            if not v:
                raise ValueError('Chưa nhập thông tin lớp giảng dạy!')
            return v
        
        @field_validator('email')
        def email_validation(cls, v):
            if not v:
                raise ValueError('Chưa nhập thông tin email!')
            return v
        
    class TeacherShowSchema(BaseModel):
        name: Optional[str] = None
        lesson: Optional[str] = None
        class_room: Optional[str] = None
        year_id: Optional[int] = None
        grade_id: Optional[int] = None

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

        @field_validator('year_id', 'grade_id', mode='before')
        def int_validation(cls, v):
            if v in ['', None]:
                return 
            
            return v

    class TeacherUpdateSchema(BaseModel):
        name: str
        lesson_id: int
        class_room_id: Optional[int] | None
        teach_class: list
        tel: str
        add: str
        email: EmailStr
        year_id: int

        @field_validator('name')
        def name_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập thông tin tên hoặc môn học!')
            elif re.search(r"[\d~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Tên không được chứa số và ký tự đặc biệt!")
            return v

        @field_validator('tel')
        def tel_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập thông tin số điện thoại!')
            elif not re.fullmatch(r'\d{10}', v):
                raise ValueError('Số điện thoại chỉ được chứa 10 chữ số!')
            return v

        @field_validator('teach_class')
        def class_room_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập thông tin lớp giảng dạy!')
            
            return v
        
        @field_validator('add')
        def add_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập thông tin địa chỉ!')
            
            elif re.search(r"[~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Thông tin địa chỉ không được ký tự đặc biệt!")
            return v
        
        @field_validator('class_room_id', mode='before')
        def class_room_validation(cls, v):
            if v in ['', 'null', 'None']:
                return None
            return v
                       
        @field_validator('lesson_id', mode='before')
        def lesson_validation(cls, v):
            if v in ['', None]:
                raise ValueError('Chưa nhập thông tin môn học!')
            return v
        
        @field_validator('year_id')
        def year_id_validation(cls, v):
            if v in ['', None]:
                raise ValueError('Hệ thống chưa set niên khóa!')
            return v