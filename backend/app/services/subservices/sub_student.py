from app.utils import generate_password
from app.exceptions import CustomException, NotFound_Exception
from werkzeug.security import generate_password_hash

class Student_Subservices:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo

    def add_student(self, data):
        student = self.repo.add_student(data)
        return student

    def generate_student_code(self, data):
        last_code = self.repo.student_last_code()
        student_code = f"BDV{data['year'][2:4]}{last_code:04d}"
        return student_code

    def add_user(self, data):
        #Create username/password/role
        password = generate_password(length=8)
        new_user = {'username': data.lower(),
                    'password': generate_password_hash(password),
                    'tmp_password': password,
                    'role': 'Student'}
        
        user = self.repo.add_user(new_user)
        return user
    
    def dup_student_code(self, data):
        existing = self.repo.check_student_code(data)
        if existing:
            raise CustomException('Trùng student code!')
        
    def get_lessons_id_by_grade_id(self, data):
        lessons_id = self.repo.get_lessons_id_by_grade_id(data)
        if not lessons_id:
            raise FileNotFoundError('Không tìm thấy lessons ID')
        
        return lessons_id
    
    def add_to_student_class(self, data):
        self.repo.student_class(data)

    def show_student_by_grade(self, data):
        result = self.repo.show_student_by_grade(data)
        return result

