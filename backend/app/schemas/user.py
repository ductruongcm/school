from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional, List
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
                raise ValueError("Họ và tên không được chứa số và ký tự đặc biệt!")
            return v
        
        @field_validator('add')
        def str_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập thông tin địa chỉ!')
            
            if re.search(r"[~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Địa chỉ không được chứa ký tự đặc biệt!")
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
                raise ValueError('Username không hợp lệ!')
            return v
        
        @field_validator('role')
        def role_validator(cls, v):
            if not v:
                return
            elif not re.match(r'^[A-Za-z]+$', v):
                raise ValueError('Role không hợp lệ!')
            return v
        
    class UserInfoUpdateSchema(BaseModel):
        email: Optional[EmailStr] = None 
        tel: Optional[str] = None   
        add: Optional[str] = None

        @field_validator('add')
        def add_validate(cls, v):
            if not v:
                raise ValueError('Địa chỉ không được bỏ trống!')
            
            elif re.search(r"[~!@#$%^&*()_+=`,.<>?-]+", v):
                raise ValueError("địa chỉ không được chứa số và ký tự đặc biệt!")
            return v
        
        @field_validator('tel')
        def tel_validator(cls, v):
            if not v:
                raise ValueError('Số điện thoại không được bỏ trống!')
            
            elif not re.fullmatch(r'\d{10}', v):
                raise ValueError('Số điện thoại chỉ được chứa 10 chữ số')
            return v
    
class StudentSchemas:
    class StudentItem(BaseModel):
        lesson_id: int
        score_1: float
        score_2: float

        @field_validator('score_1', 'score_2')
        def score_validates(cls, v):
            if 0 > v or v > 10:
                raise ValueError('Điểm số phải từ 0 đến 10!')
            return v

    class StudentCreate(UserSchemas.User):
        tel: Optional[str] | None
        gender: str
        bod: Optional[date] = None
        year_id: int
        year: str
        grade: int
        conduct: bool
        lesson: List['StudentSchemas.StudentItem']
        note: str
        absent_day: Optional[int]
        
        @field_validator('bod', 'absent_day', mode='before')
        def bod_cls_room_validate(cls, v):
            if v in ['', 'null']:
                return 
            return v
        
        @field_validator('conduct', mode='before')
        def conduct_bool_validate(cls, v):
            if v in ['', 'null']:
                raise ValueError('Chưa nhập hạnh kiểm của học sinh!')
            
            return v
        
        @field_validator('year_id', mode='before')
        def validate_year_id(cls, v):
            if v in ['', 'null']:
                raise ValueError('Chưa chọn niên khóa đăng ký cho học sinh!')
            
            return v
        
        @field_validator('grade', mode='before')
        def validate_grade(cls, v):
            if v in ['', 'null']:
                raise ValueError('Chưa chọn khối lớp đăng ký cho học sinh!')
            
            return v
    
    class StudentShow(BaseModel):
        year_id: Optional[int] = Field(default = None)
        grade: Optional[int] = Field(default = None)
        class_room_id: Optional[int] = Field(default = None)
       
        @field_validator('grade', 'year_id', 'class_room_id', mode='before')
        def int_validator(cls, v):
            if v in ['', 'None', 'null']:
                return 
            return v
        
    class StudentShowForAssignment(BaseModel):
        grade: Optional[int]
        review_status: Optional[bool]
        status: Optional[str] = None

        @field_validator('grade', mode='before')
        def int_validator(cls, v):
            if v in ['', 'None', 'null']:
                return 
            return v
        
        @field_validator('status')
        def validate_status(cls, v):
            if v not in ['Lên lớp', 'Lưu ban', 'Bảo lưu', '']:
                return None
            return v
    
    class StudentShowForScores(BaseModel):
        semester_id: Optional[int] = Field(default=None)
        year_id: Optional[int] = Field(default=None)
        class_room_id: Optional[int] = Field(default=None)
        lesson_id: Optional[int] = Field(default=None)

    class StudentUpdate(BaseModel):
        student_id: int
        name: Optional[str] = None
        tel: Optional[str] = None
        add: Optional[str] = None
        BOD: Optional[date] = None
        gender: Optional[str] = None
        note: Optional[str] = None
        class_room_id: Optional[int] = None
        year_id: Optional[int] = None

        @field_validator('name')
        def name_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập họ và tên!')
            
            elif re.search(r"[\d~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Họ và tên không được chứa số và ký tự đặc biệt!")
            
            return v
        
        @field_validator('BOD', mode='before')
        def bod_validator(cls, v):
            if v in ['', 'null']:
                raise ValueError('Chưa chọn ngày sinh!')
            
            return v
        
        @field_validator('add')
        def str_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập thông tin địa chỉ!')
            
            elif re.search(r"[~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Địa chỉ không được chứa ký tự đặc biệt!")
            return v
        
        @field_validator('tel')
        def tel_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập thông tin địa chỉ!')
            elif not re.fullmatch(r'\d{10}', v):
                raise ValueError('Số điện thoại chỉ được chứa 10 chữ số')
            return v
    
    class StudentReview(BaseModel):
        student_id: int
        status: str

        @field_validator('status')
        def status_validate(cls, v):
            if v not in ['Chờ xét duyệt', 'Chờ xếp lớp', '', 'Lên lớp', 'Lưu ban', 'Bảo lưu']:
                return ValueError('Status không hợp lệ!')
            return v

    class StudentAssignmentItem(BaseModel):
        class_room_id: int
        student_id: int

    class StudentAssignment(BaseModel):
        year_id: int
        student_assign_list: List['StudentSchemas.StudentAssignmentItem']
    
    class TransferStudent(BaseModel):
        class_room_id: int
        class_room: str
        year_id: int
    
class TeacherSchemas:    
    class TeacherCreateSchema(UserSchemas.User):
        username: str
        tel: str
        teaching_class_ids: Optional[list]
        class_room: Optional[str] | None
        class_room_id: Optional[int] | None
        email: EmailStr
        lesson_id: int
        year_id: int

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
        grade: Optional[int] = None

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

        @field_validator('year_id', 'grade', mode='before')
        def int_validation(cls, v):
            if v in ['', None]:
                return 
            
            return v

    class TeacherUpdateSchema(BaseModel):
        name: Optional[str] = None
        lesson_id: Optional[int] = None
        class_room_id: Optional[int] = None
        teach_class: Optional[list] = None
        tel: Optional[str] = None
        add: Optional[str] = None
        email: Optional[EmailStr] = None
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