from app.exceptions import CustomException, NotFound_Exception, DuplicateException

class Academic_Validation:
    def __init__(self, db, repo):
        self.academic_repo = repo(db).academic_get
    
    def check_dup_lesson(self, data):
        existing = self.academic_repo.check_lesson(data)
        if existing:
            raise DuplicateException('Môn học đã có!')
        
    def check_dup_year(self, data):
        existing = self.academic_repo.get_year_by_year_code(data)
        if existing:
            raise DuplicateException('Niên khóa đã có!')
        
    def check_dup_semester(self, data):
        existing = self.academic_repo.check_semester(data)
        if existing:
            raise DuplicateException('Học kỳ đã có!')
        
    def check_dup_grade(self, data):
        existing = self.academic_repo.get_grade_by_grade(data)
        if existing:
            raise DuplicateException('Khối lớp đã có!')

    def check_dup_class_room(self, data):
        existing = self.academic_repo.check_class_room(data)
        if existing:
            raise DuplicateException('Lớp học đã có, hãy chọn tên khác!')
        
    def check_dup_score_type(self, data):
        existing = self.academic_repo.get_score_type(data)
        if existing:
            raise DuplicateException('Loại điểm số bị trùng!')

    def check_year(self, data):
        if data.get('year_code') != None:
            if data['year_code'] != self.academic_repo.get_year_by_id(data).year:
                raise CustomException('Niên khóa không hợp lệ!')

    def validate_grade(self, data):
        if data.get('grade') != None:
            grade = self.academic_repo.get_grade_by_grade(data)
            if not grade:
                raise NotFound_Exception('Không tìm thấy grade!')
        
    def validate_class_room_id(self, data):
        if data.get('class_room_id') != None:
            class_room = self.academic_repo.get_class_room_by_id(data)
            if not class_room:
                raise NotFound_Exception('Không tìm thấy ID lớp học!')
    
    def validate_year_id(self, data):
        if data.get('year_id') != None:
            year = self.academic_repo.get_year_by_id(data)
            if not year:
                raise NotFound_Exception('Chưa thiết lập niên khóa!')
    
    def validate_lesson_id(self, data):
        if data.get('lesson_id') != None:
            lesson = self.academic_repo.get_lesson_by_id(data)
            if not lesson:
                raise NotFound_Exception('Không tìm thấy ID môn học!')
    
    def validate_semester_id(self, data):
        if data.get('semester_id') != None:
            semester = self.academic_repo.get_semester_by_id(data)
            if not semester:
                raise NotFound_Exception('Không tìm thấy ID học kỳ!')
    
    def validate_score_type_id(self, data):
        if data.get('score_type_id') != None:
            score_type = self.academic_repo.get_score_type_by_id(data)
            if not score_type:
                raise NotFound_Exception('Không tìm thấy Score type!')

class Academic_Teacher_Validation:
    def __init__(self, db, repo):
        self.repo = repo(db)
        self.academic_teacher_repo = self.repo.academic_teacher

    def check_existing_teacher_in_teaching_class(self, data):
        check_teaching_class = self.academic_teacher_repo.get_teacher_by_lesson_class_year(data)
        if bool(any(check_teaching_class)): 
            raise DuplicateException('Lớp học đã có giáo viên bộ môn này!')
        
    def check_existing_teacher_in_home_class(self, data):
        check_home_class = self.academic_teacher_repo.get_teacher_by_class_room(data)
        pass
    
class User_Validation:
    def __init__(self, db, repo):
        self.repo = repo(db)
        self.user_repo = self.repo.user

    def check_dup_username(self, data):
        existing = self.user_repo.get_user_by_username(data)
        if existing:
            raise DuplicateException('Username đã có người sử dụng, hãy đổi username khác!')
    
    def validate_user_id(self, data):
        user = self.user_repo.get_user_by_id(data)
        if not user:
            raise NotFound_Exception('ID user không hợp lệ!')
        
    def validate_password(self, data):
        if data['password'] != data['repassword']:
            raise CustomException('Xác nhận mật khẩu không chính xác!')
        
class Teacher_Validation:
    def __init__(self, db, repo):
        self.teacher_repo = repo(db).teacher

    def validate_teacher_id(self, data):
        teacher = self.teacher_repo.get_teacher_by_id(data)
        if not teacher:
            raise NotFound_Exception('ID teacher không hợp lệ!')
