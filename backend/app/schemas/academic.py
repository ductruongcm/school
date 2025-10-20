from pydantic import BaseModel, field_validator
from typing import Optional
import re

class AcademicSchemas:
    class Year(BaseModel):
        year: str

        @field_validator('year')
        def year_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập niên khóa!')
            
            elif not re.fullmatch(r'[\d\s-]+', v):
                raise ValueError('Niên khóa không được chứa ký tự đặc biệt và chữ cái. VD: 2025 - 2026')  
            return v
        
    class YearID(BaseModel):
        year_id: int

        @field_validator('year_id')
        def year_id_validation(cls, v):
            if v in ['', None]:
                raise ValueError('Chưa set niên khóa ở công cụ năm học!!')

            return v

    class Grade(BaseModel):
        grade: str

        @field_validator('grade')
        def grade_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập khối lớp!')
            elif re.search(r"[~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError('Không được nhập ký tự đặc biệt!!')
            return v

    class GradeID(BaseModel):
        grade_id: int
                
        @field_validator('grade_id')
        def grade_id_validator(cls, v):
            if v in ['', None]:
                raise ValueError('Khối lớp học không được bỏ trống')
            return v
        
    class Classroom(YearID):
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

    class Semester(YearID):
        semester: str
        
        @field_validator('semester')
        def semester_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập học kỳ!')
            
            elif v not in ['HKI', 'HKII', 'Học kỳ I', 'Học kỳ II']:
                raise ValueError('Học kỳ nên là HKI, HKII/Học Kỳ I, Học kỳ II') 
                
            return v
        
    class SemesterID(BaseModel):
        semester_id: int    
       
        @field_validator('semester_id')
        def semester_id_validator(cls, v):
            if not v:
                raise ValueError('Chưa chọn học kỳ!')

            return v        

    class Lesson(YearID, GradeID):
        lesson: str

        @field_validator('lesson')
        def lesson_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập môn học!')
            
            elif re.search(r"[\d~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Thông tin không được chứa số và ký tự đặc biệt!")
            return v
    
    class ClassLesson(GradeID):
        lesson_id: int

        @field_validator('lesson_id')
        def grade_id_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập Khối lớp!')

            return v
    
    class Schedule(YearID, SemesterID):
        class_room_id: int

        @field_validator('class_room_id')
        def grade_id_validator(cls, v):
            if not v:
                raise ValueError('Chưa chọn lớp!')

            return v

    class Scores(Semester, SemesterID):
        pass

    class SemesterUpdate(Semester, SemesterID):
        pass
               
    class LessonUpdate(Lesson):
        lesson_id: int
        
        @field_validator('lesson_id')
        def lesson_id_validator(cls, v):
            if v in ['', None]:
                raise ValueError('ID môn học không được bỏ trống')
            return v
        
    class ClassUpdate(Classroom):
        class_room_id: int
        
        @field_validator('class_room_id')
        def lesson_id_validator(cls, v):
            if v in ['', None]:
                raise ValueError('ID lớp học không được bỏ trống')
            return v

    class AssignStudent(Classroom):
        student_ids: list
        class_room: str
        
class AcademicShowSchemas:
    class YearShow(BaseModel):
        year: Optional[str] = None
        is_active: Optional[bool] = None

        @field_validator('year')
        def year_validator(cls, v):
            if not v:  # None hoặc ''
                return None
            if not re.fullmatch(r'[\d\s-]+', v):
                raise ValueError('Niên khóa không được chứa ký tự đặc biệt và chữ cái. VD: 2025 - 2026')
            return v
        
    class YearId(BaseModel):
        year_id: int

    class GradeId(BaseModel):
        grade_id: int | None

        @field_validator('grade_id', mode='before')
        def parse_null_int(cls, v):
            if v in ['', 'null', 'None']:
                return None
            return v

    class ClassroomShow(YearId, GradeId):
        class_room: Optional[str] = None

        @field_validator('class_room')
        def class_room_validator(cls, v):    
            if not v:
                return None
            
            elif len(v) > 3:
                raise ValueError('Nhập lớp học không đúng!!')

            elif not re.search(r'[\dA-Za-z]', v):
                raise ValueError('Lớp học không chứa ký tự đặc biệt!!')
            return v
        
    class LessonShow(GradeId, YearId):
        lesson: Optional[str] = None
    
        @field_validator('lesson')
        def lesson_validator(cls, v):
            if not v:
                return None
            
            if re.search(r"[\d~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Thông tin không được chứa số và ký tự đặc biệt!")
            return v

    class SemesterShow(BaseModel):
        semester: Optional[str] = None
            
        @field_validator('semester')
        def semester_validator(cls, v):
            if not v:
                return 
            
            if v not in ['HKI', 'HKII', 'Học kỳ I', 'Học kỳ II']:
                raise ValueError('Học kỳ nên là HKI, HKII/Học Kỳ I, Học kỳ II')
            return v
        
    class GradeShow(BaseModel):
        grade: Optional[str] = None

        @field_validator('grade')
        def grade_validator(cls, v):
            if re.search(r"[~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError('Không được nhập ký tự đặc biệt!!')
            return v
    
    class UserList(YearId):
        pass
    
    class TeachLessClass(YearId):
        pass

class AcademicUpdateSchemas:
    class YearId(BaseModel):
        year_id: int

        @field_validator('year_id')
        def grade_id_validator(cls, v):
            if v in ['', None]:
                raise ValueError('Niên khóa không được bỏ trống')
            return v

    class GradeId(BaseModel):
        grade_id: int
                
        @field_validator('grade_id')
        def grade_id_validator(cls, v):
            if v in ['', None]:
                raise ValueError('Khối lớp học không được bỏ trống')
            return v
        
    class SemesterUpdate(YearId):
        semester_id: int
        semester: str

        @field_validator('semester')
        def semester_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập học kỳ!')
            
            elif v not in ['HKI', 'HKII', 'Học kỳ I', 'Học kỳ II', 'Hè', 'Phụ đạo']:
                raise ValueError('Học kỳ nên là HKI, HKII/Học Kỳ I, Học kỳ II') 
            return v
        
    class LessonUpdate(GradeId, YearId):
        lesson: str
        lesson_id: int

        @field_validator('lesson')
        def lesson_validator(cls, v):
            if not v:
                raise ValueError('Thông tin môn học không được bỏ trống!')
            
            if re.search(r"[\d~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Thông tin không được chứa số và ký tự đặc biệt!")
            return v
        
        @field_validator('lesson_id')
        def lesson_id_validator(cls, v):
            if v in ['', None]:
                raise ValueError('ID môn học không được bỏ trống')
            return v
        
    class ClassUpdate(YearId):
        class_room: str
        class_room_id: int
        
        @field_validator('class_room')
        def class_room_validator(cls, v):
            if not v:
                raise ValueError('Lớp học không được bỏ trống!')
            
            if len(v) > 3:
                raise ValueError('Nhập lớp học không đúng!!')

            elif not re.search(r'[\dA-Za-z]', v):
                raise ValueError('Lớp học không chứa ký tự đặc biệt!!')
            return v
        
        @field_validator('class_room_id')
        def lesson_id_validator(cls, v):
            if v in ['', None]:
                raise ValueError('ID lớp học không được bỏ trống')
            return v
    
    class AssignStudent(YearId):
        student_ids: list
        class_room: str
        @field_validator('class_room')
        def class_room_validator(cls, v):
            if not v:
                raise ValueError('Lớp học không được bỏ trống!')
            
            if len(v) > 3:
                raise ValueError('Nhập lớp học không đúng!!')

            elif not re.search(r'[\dA-Za-z]', v):
                raise ValueError('Lớp học không chứa ký tự đặc biệt!!')
            return v
