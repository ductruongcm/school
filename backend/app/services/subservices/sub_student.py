from app.exceptions import NotFound_Exception, DuplicateException

class Student_Subservice:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo
    
    def check_dup_student_code(self, data):
        existing = self.repo.get_student_by_student_code(data)
        if existing:
            raise DuplicateException('Trùng student code!')
        
    def get_lessons_id_by_grade_id(self, data):
        lessons_id = self.repo.get_lessons_id_by_grade_id(data)
        if not lessons_id:
            raise NotFound_Exception('Không tìm thấy lessons ID')
        
        return lessons_id
    
    def add_to_student_class(self, data):
        self.repo.student_class(data)

    def show_student_by_grade(self, data):
        result = self.repo.show_student_by_grade(data)
        return result
    
    def get_student_info_by_student(self, data):
        info = self.repo.get_student_info_by_student(data)
        if not info:
            raise NotFound_Exception('Không tìm thấy student id!')
        return info
    
    def get_student_by_id(self, data):
        student = self.repo.get_student_by_id(data)
        if not student:
            raise NotFound_Exception('Không tìm thấy student id!')
        return student
    
    def add_conduct_last_year(self, data):
        #student_id, conduct, year_id
        data['year_id'] = data['year_id'] - 1
        pass
    