from .subservices.sub_student import Student_Subservice
from app.exceptions import NotFound_Exception

class StudentServices:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.student_repo = self.repo.student
        self.student_subservices = Student_Subservice(self.db, self.student_repo)

    def handle_get_student_by_id(self, data: dict):
        student = self.student_repo.get_student_by_id(data)
        if not student:
            raise NotFound_Exception('ID học sinh không hợp lệ!')
        return student
    
    def handle_get_student_ids_by_year_and_class_room(self, data):
        students = self.student_repo.get_student_ids_by_year_and_class_room(data)
        if not students:
            raise NotFound_Exception('Không lấy được danh sách học sinh!')
        
        return students
    
    def handle_get_student_info_by_student(self, data):
        student_info = self.student_repo.get_student_info_by_student(data)
        if not student_info:
            raise NotFound_Exception('ID học sinh không hợp lệ!')
        return student_info

    def handle_add_student(self, data:dict):
        #Tạo student
        student = self.student_repo.insert_student(data)
        return student
    
    def handle_generate_student_code(self, data):
        last_code = self.student_repo.student_last_code()
        student_code = f"BDV{data['year'][2:4]}{last_code:04d}"

        #check dup
        self.student_subservices.check_dup_student_code(student_code)
        return student_code
    
    def handle_show_students(self, data: dict):
        result = self.student_repo.show_students_with_info(data)
        keys = ['student_id', 'name', 'gender', 'BOD', 'tel', 'add', 'grade', 'note', 'class_room_id']

        return [dict(zip(keys, values)) for values in result]

    def handle_update_student_info(self, data):
        if any(key for key in data if key in ['tel', 'add']):
            detail_changes = []
            student_info = self.handle_get_student_info_by_student(data)

            if data.get('tel'):
                old_tel = student_info.tel
                student_info.tel = data['tel']
                detail_changes.append(f'SĐT: {old_tel} => {data['tel']}')

            if data.get('add'):
                old_add = student_info.add
                student_info.add = data['add']
                detail_changes.append(f'Địa chỉ: {old_add} => {data['add']}')

        return ', '.join(detail_changes)

    def handle_show_student_info(self, data):
        result = self.student_repo.show_student_info_by_user(data)
        keys = ['name', 'tel', 'add']

        return [dict(zip(keys, values)) for values in result]
    

