from app.exceptions import CustomException, NotFound_Exception

class AcademicCheck:
    def __init__(self, check_repo):
        self.check_repo = check_repo
    
    def dup_lesson(self, data):
        existing = self.check_repo.lesson(data)
        if existing:
            raise CustomException('Môn học đã có!')
        
    def dup_year(self, data):
        existing = self.check_repo.year(data)
        if existing:
            raise CustomException('Niên khóa đã có!')
        
    def dup_semester(self, data):
        existing = self.check_repo.semester(data)
        if existing:
            raise CustomException('Học kỳ đã có!')
        
    def dup_grade(self, data):
        existing = self.check_repo.grade(data)
        if existing:
            raise CustomException('Khối lớp đã có!')

    def dup_class_room(self, data):
        existing = self.check_repo.class_room(data)
        if existing:
            raise CustomException('Lớp học đã có, hãy chọn tên khác!')


class AcademicGet:
    def __init__(self, get_repo):
        self.get_repo = get_repo

    def grade_id(self, data):
        if data['grade_id'] != None:
            grade = self.get_repo.grade_by_id(data)
            if not grade:
                raise NotFound_Exception('Không tìm thấy grade_id!')
            return grade
        
    def class_room_id(self, data):
        class_room = self.get_repo.class_room_by_id(data)
        if not class_room:
            raise NotFound_Exception('Không tìm thấy ID lớp học!')
        
        return class_room
    
    def year_id(self, data):
        year = self.get_repo.year_by_id(data)
        if not year:
            raise NotFound_Exception('Chưa thiết lập niên khóa!')
        return year
    
    def lesson_id(self, data):
        lesson = self.get_repo.lesson_by_id(data)
        if not lesson:
            raise NotFound_Exception('Không tìm thấy ID môn học!')
        
        return lesson
    
    def semester_id(self, data):
        semester = self.get_repo.semester_by_id(data)
        if not semester:
            raise NotFound_Exception('Không tìm thấy ID học kỳ!')
        return semester
        



        