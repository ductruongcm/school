from pydantic import BaseModel, field_validator
from typing import Optional
import re

class AcademicCreateSchemas:
    class YearCreateSchema(BaseModel):
        year: str

        @field_validator('year')
        def year_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập niên khóa!')
            
            elif not re.fullmatch(r'[\d\s-]+', v):
                raise ValueError('Niên khóa không được chứa ký tự đặc biệt và chữ cái. VD: 2025 - 2026')  
            return v

    class GradeCreateSchema(BaseModel):
        grade: str

        @field_validator('grade')
        def grade_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập khối lớp!')
            elif re.search(r"[~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError('Không được nhập ký tự đặc biệt!!')
            return v

    class ClassroomCreateSchema(YearCreateSchema):
        class_room: str

        @field_validator('class_room')
        def class_room_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập lớp học!')
            
            elif len(v) != 3:
                raise ValueError('Nhập lớp học không đúng!!')
            
            elif not re.search(r'[\dA-Z]', v):
                raise ValueError('Lớp học không chứa ký tự đặc biệt!!')
            return v

    class SemesterCreateSchema(YearCreateSchema):
        semester: str
        
        @field_validator('semester')
        def semester_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập học kỳ!')
            
            elif v not in ['HKI', 'HKII', 'Học kỳ I', 'Học kỳ II']:
                raise ValueError('Học kỳ nên là HKI, HKII/Học Kỳ I, Học kỳ II') 
            return v
        
    class LessonCreateSchema(BaseModel):
        lesson: str

        @field_validator('lesson')
        def lesson_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập môn học!')
            
            elif re.search(r"[\d~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Thông tin không được chứa số và ký tự đặc biệt!")
            return v

class AcademicShowSchemas:
    class YearShowSchema(BaseModel):
        year: Optional[str] = None

        @field_validator('year')
        def lesson_validator(cls, v):
            if not v:
                return 
            
            if not re.fullmatch(r'[\d -]', v):
                raise ValueError('Niên khóa không được chứa ký tự đặc biệt và chữ cái. VD: 2025 - 2026')
            return v
    
    class ClassroomShowSchema(YearShowSchema):
        class_room: Optional[str] = None

        @field_validator('class_room')
        def class_room_validator(cls, v):    
            if not v:
                return 
            
            elif len(v) > 3:
                raise ValueError('Nhập lớp học không đúng!!')

            elif not re.search(r'[\dA-Za-z]', v):
                raise ValueError('Lớp học không chứa ký tự đặc biệt!!')
            return v
        
    class LessonShowSchema(ClassroomShowSchema):
        lesson: Optional[str] = None
    
        @field_validator('lesson')
        def lesson_validator(cls, v):
            if not v:
                return 
            
            if re.search(r"[\d~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Thông tin không được chứa số và ký tự đặc biệt!")
            return v

    class SemesterShowSchema(BaseModel):
        semester: Optional[str] = None
            
        @field_validator('semester')
        def semester_validator(cls, v):
            if not v:
                return 
            
            if v not in ['HKI', 'HKII', 'Học kỳ I', 'Học kỳ II']:
                raise ValueError('Học kỳ nên là HKI, HKII/Học Kỳ I, Học kỳ II')
            return v
        
    class GradeShowSchema(BaseModel):
        grade: Optional[str] = None

        @field_validator('grade')
        def grade_validator(cls, v):
            if re.search(r"[~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError('Không được nhập ký tự đặc biệt!!')
            return v
    