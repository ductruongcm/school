from pydantic import BaseModel, field_validator, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date
import re


class AcademicSchemas:
    class Year(BaseModel):
        start_date: date
        end_date: date

        @field_validator('start_date', 'end_date', mode='before')
        def validate_date(cls, v):
            if v in ['', 'null']:
                raise ValueError('Chưa chọn ngày dự kiến cho năm học mới!')
            return v
        
    class YearID(BaseModel):
        year_id: int

        @field_validator('year_id')
        def year_id_validation(cls, v):
            if v in ['', None]:
                raise ValueError('Chưa set niên khóa ở công cụ năm học!!')

            return v

    class Grade(BaseModel):
        grade: Optional[int] 
        grade_status: Optional[bool] 

        @field_validator('grade', mode='before')
        def grade_validator(cls, v):
            if v in ['', 'null']:
                raise ValueError('Chưa nhập khối lớp')
            
            try:
                v = int(v)
            
            except ValueError:
                raise ValueError('Khối lớp chỉ được chứa số!')
            
            return v  
        
        @field_validator('grade_status', mode='before')
        def status_validator(cls, v):
            if v in ['', 'null']:
                raise ValueError('Chưa có trạng thái của khối lớp!')
            
            return v

    class GradeID(BaseModel):
        grade_id: int
                
        @field_validator('grade_id', mode='before')
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
        weight: int
        
        @field_validator('semester')
        def semester_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập học kỳ!')
            
            elif v not in ['HKI', 'HKII', 'Học kỳ I', 'Học kỳ II']:
                raise ValueError('Học kỳ nên là HKI, HKII/Học Kỳ I, Học kỳ II') 
                
            return v
        
    class SemesterID(BaseModel):
        semester_id: int    
       
        @field_validator('semester_id', mode='before')
        def semester_id_validator(cls, v):
            if v in ['', 'null']:
                raise ValueError('Chưa chọn học kỳ!')

            return v        

    class Lesson(BaseModel):
        lesson: str
        grade: int
        is_visible: Optional[bool] = None
        is_folder: Optional[bool] = None
        is_schedule: Optional[bool] = None

        @field_validator('lesson')
        def lesson_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập môn học!')
            
            elif re.search(r"[\d~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Thông tin không được chứa số và ký tự đặc biệt!")
            return v

        @field_validator('is_visible', 'is_schedule', 'is_folder', mode='before')
        def bool_validator(cls, v):
            if v in ['', 'null', 'None']:
                return 
            return v
        
        @field_validator('grade', mode='before')
        def grade_validator(cls, v):
            if v in ['', 'null']:
                raise ValueError('Chưa chọn khối lớp!')
            return v
        
    class ScheduleItem(BaseModel):
        lesson_id: Optional[int] = None

        @field_validator('lesson_id', mode='before')
        def lesson_id_validator(cls, v):
            if v == '':
                return 
            return v
   
    class Schedule(YearID, SemesterID):
        class_room_id: int
        schedules: Dict[str, Dict[str, 'AcademicSchemas.ScheduleItem']]
        
        @field_validator('class_room_id', mode='before')
        def class_room_id_validate(cls, v):
            if v in ['', 'null']:
                raise ValueError('Chưa chọn lớp để tạo thời khóa biểu!')
            return v

    class AttendenceItem(BaseModel):
        student_id: int
        status: str
        note: Optional[str]

        @field_validator('status')
        def validate_status(cls, v):
            if v not in ['P', 'E', 'A']:
                raise ValueError('Dữ liệu không hợp lệ!')
            return v
        
    class Attendence(YearID, SemesterID):
        day: date
        students: List['AcademicSchemas.AttendenceItem']

    class Scores(Semester, SemesterID):
        pass

    class SemesterUpdate(Semester, SemesterID):
        pass
               
    class LessonUpdate(BaseModel):
        lesson_id: int
        year_id: int
        lesson: Optional[str] = None
        grade: Optional[int] = None
        is_visible: Optional[bool] = None
        is_folder: Optional[bool] = None
        is_schedule: Optional[bool] = None
        
        @field_validator('lesson_id')
        def lesson_id_validator(cls, v):
            if v in ['', None]:
                raise ValueError('ID môn học không hợp lệ')
            return v
        
        @field_validator('lesson')
        def lesson_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập môn học!')
            
            elif re.search(r"[\d~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Thông tin không được chứa số và ký tự đặc biệt!")
            return v
        
    class ClassUpdate(Classroom):
        class_room_id: int
        
        @field_validator('class_room_id')
        def lesson_id_validator(cls, v):
            if v in ['', None]:
                raise ValueError('ID lớp học không được bỏ trống')
            return v
        
    class Lessons_Class(YearID):
        pass

    class ScoreTypes(BaseModel):
        score_type: str
        weight: int

        @field_validator('score_type')
        def validate_score_type(cls, v):
            if v in ['', 'null']:
                raise ValueError('Không được bỏ trống loại điểm số!')
            
            return v

        @field_validator('weight', mode='before')
        def validate_weight(cls, v):
            if v in ['', 'null']:
                raise ValueError('Hệ số không được bỏ trống!')
            
            try: 
                return int(v)
            
            except:
                raise ValueError('Hệ số chỉ được chứ số, VD: 1 hoặc 2')

class AcademicShowSchemas:
    class YearShow(BaseModel):
        is_active: Optional[bool] = Field(default=None)

        @field_validator('is_active', mode='before')
        def validate_bool(cls, v):
            if v in ['', 'null']:
                return None
            
            return v
        
    class YearId(BaseModel):
        year_id: int

        @field_validator('year_id', mode='before')
        def year_id_validator(cls, v):
            if v in ['', 'null']:  # None hoặc ''
                raise ValueError('Chưa thiết lập niên khóa!')
     
            return v

    class SemesterId(BaseModel):
        semester_id: int

        @field_validator('semester_id', mode='before')
        def semester_id_validator(cls, v):
            if v in ['', 'null']:  # None hoặc ''
                raise ValueError('Chưa chọn học kỳ!')
     
            return v

    class ClassroomId(BaseModel):
        class_room_id: int

        @field_validator('class_room_id', mode='before')
        def class_room_id_validator(cls, v):
            if v in ['', 'null']:
                raise ValueError('Chưa chọn lớp học!')
            return v

    class LessonId(BaseModel):
        lesson_id: int

        @field_validator('lesson_id', mode='before')
        def lesson_id_validator(cls, v):
            if v in ['', 'null']:  # None hoặc ''
                raise ValueError('Chưa chọn môn học!')
     
            return v

    class Grade(BaseModel):
        grade: int | None
        @field_validator('grade', mode='before')
        def parse_null_int(cls, v):
            if v in ['', 'null', 'None']:
                return None
            return v

    class ClassroomShow(Grade):
        semester_id: Optional[int] = Field(default=None)
        
    class ClassRoomShowForAssignment(ClassroomShow):
        status: Optional[str]

        @field_validator('status')
        def validate_status(cls, v):
            if v not in ['Lên lớp', 'Lưu ban', 'Bảo lưu', '']:
                raise ValueError('Kết quả học tập không hợp lệ!')
            return v
        
    class LessonShow(Grade):
        is_visible: Optional[bool] | None
        is_folder: Optional[bool] | None
        is_schedule: Optional[bool] | None

        @field_validator('is_visible', 'is_folder', 'is_schedule', mode='before')
        def boolean_validator(cls, v):
            if v in ['', 'null']:
                return
            return v
        
    class LessonShowByIsvisible(Grade):
        pass

    class SemesterShow(BaseModel):
        is_active: Optional[bool] = None
        
        @field_validator('is_active', mode='before')
        def is_active_validator(cls, v):
            if v in ['', 'null']:
                return
            return v
        
    class GradeShow(BaseModel):
        grade_status: Optional[bool] = Field(default=None)

        @field_validator('grade_status', mode='before')
        def grade_validator(cls, v):
            if v in['', 'null']:
                return 
            
            return v

    class UserList(YearId):
        pass
    
    class TeachLessClass(YearId):
        teacher_id: int
        
        @field_validator('teacher_id')
        def teacher_id_validator(cls, v):
            if v in ['', None]:
                raise ValueError('ID giáo viên không được bỏ trống')
            return v

    class Scores(YearId, SemesterId, ClassroomId):
        pass

    class Schedule(YearId, SemesterId):
        class_room_id: Optional[int] = Field(default=None)
        day: Optional[date] = Field(default_factory=date.today)

        @field_validator('class_room_id', mode='before')
        def validate_class_id(cls, v):
            if v in ['', 'null']:
                return
            
            return v
        
    class ClassInfoForDashboard(YearId, SemesterId):
        day: Optional[date] = Field(default_factory=date.today)

    class ScheduleForDashBoard(YearId, SemesterId):
        pass

    class StudentScores(YearId, SemesterId):
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
                raise ValueError('ID Khối lớp học không được bỏ trống')
            return v
        
    class Grade(GradeId):
        grade: Optional[int] = None
        grade_status: Optional[bool] = None

        @field_validator('grade', mode='before')
        def grade_validator(cls, v):
            try:
                v = int(v)
            except ValueError:
                raise ValueError('Khối lớp không được bỏ trống và chỉ được chứa số!')      
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
        is_visible: Optional[bool] | None
        add_folder: Optional[bool] | None

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
        
        @field_validator('is_visible', 'add_folder', mode='before')
        def boolean_validator(cls, v):
            if v in ['', 'null']:
                return 
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

    class ScoresItem(BaseModel):
        student_id: int
        scores: Optional[Dict[int, Dict[int, Any]]] = Field(default=None)
        note: Optional[str] = None

        @validator('scores')
        def validate_scores(cls, v):
            for score_type_id, attempts in v.items():
                for attempt, score in attempts.items():
                    if score == '':
                        attempts[attempt] = None

                    try:
                        score = float(score)
                            
                    except:
                        raise ValueError('Điểm số phải là số!')
                    
                    if 0 > score or score > 10:
                        raise ValueError('Điểm sổ nằm trong dãy từ 0 đến 10!')
                            
                    attempts[attempt] = score
                    
            return v
        
    class BaseScores(YearId):
        class_room_id: int
        
        @field_validator('class_room_id', mode='before')
        def validate_class_room_id(cls, v):
            if v in ['', 'null']:
                raise ValueError('Chưa chọn lớp học!')

            return v

    class Scores(YearId):
        lesson_id: int
        semester_id: int
        students: List['AcademicUpdateSchemas.ScoresItem']

    class ScoreTypes(BaseModel):
        score_type_id: int
        score_type: Optional[str] = None
        weight: Optional[int] = None

        @field_validator('weight', mode='before')
        def validate_weight(cls, v):
            if v in ['', 'null']:
                raise ValueError('Hệ số không được bỏ trống')
            
            try:
                return int(v)
            
            except:
                raise ValueError('Hệ số chỉ được chứa số!')
        
        @field_validator('score_type')
        def validate_score_type(cls, v):
            if v in ['', 'null']:
                raise ValueError('Điểm số không được bỏ trống!')
            
            return v

    class SummaryPeriod(BaseScores):
        students : List['AcademicUpdateSchemas.SummaryItem']

        @validator('students')
        def validate_students(cls, v):
            for item in v:
                if item.conduct in ['', None]:
                    raise ValueError('Chưa đánh giá hạnh kiểm học sinh đầy đủ!')
                
                if item.absent_day in ['', None]:
                    item.absent_day = 0

                elif item.absent_day < 0:
                    raise ValueError('Số ngày nghỉ không hợp lệ!')

            return v

    class SummaryItem(BaseModel):
        student_id: int
        absent_day: Optional[int]
        conduct: Optional[bool]
        note: Optional[str]
        status: Optional[str]
        
    class SummaryLessonPeriod(BaseScores):
        lesson_id: int
        semester_id: int

    class SummaryYear(BaseModel):
        students : List['AcademicUpdateSchemas.SummaryItem']
        class_room_id: int
        
        @validator('students')
        def validate_students(cls, v):
            for item in v:
                if item.conduct in ['', None]:
                    raise ValueError('Chưa đánh giá hạnh kiểm học sinh đầy đủ!')
                
                if item.absent_day in ['', None]:
                    item.absent_day = 0

                elif item.absent_day < 0:
                    raise ValueError('Số ngày nghỉ không hợp lệ!')

            return v

    class RetestScoreItem(BaseModel):
        score: float

        @field_validator('score')
        def validate_score(cls, v):
            try:
                v = float(v)

            except:
                raise ValueError('Điểm số phải là số')
            
            if v < 0 or v > 10:
                raise ValueError('Điểm số trong phạm từ 0 đến 10!')

            return v
            
    class RetestScore(BaseModel):
        student_id: int
        lessons: Dict[int, 'AcademicUpdateSchemas.RetestScoreItem']
