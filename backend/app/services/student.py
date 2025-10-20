from .subservices.sub_student import Student_Subservices
from .subservices.sub_academic import AcademicGet

class StudentServices:
    def __init__(self, db, student_repo, get_repo):
        self.db = db
        self.student_repo = student_repo(db)
        self.get_repo = get_repo(db)
        self.student_subservices = Student_Subservices(self.db, self.student_repo)
        self.academic_get = AcademicGet(self.get_repo)

    def handle_add_student(self, data:dict):
        #Tạo student
        student = self.student_subservices.add_student(data)
        #generate student_code và check dup
        student_code = self.student_subservices.generate_student_code(data)
        self.student_subservices.dup_student_code(student_code)
        #Tạo user
        user = self.student_subservices.add_user(student_code)
        #Link user và student
        student.student_code = student_code
        student.user_id = user.id
        #add student_id, grade_id, class_room_id to student_class
        data['student_id'] = student.id
        self.student_subservices.add_to_student_class(data)
    
        self.db.session.commit()
        #export name, class_room, username, password to Excel file
        export_data = {
            'name': student.name,
            'class_room': data['class_room'],
            'username': user.username,
        }

        return export_data
    
    def handle_show_student_by_grade(self, data: dict):
        #check grade_id
        self.academic_get.grade_id(data)

        result = self.student_subservices.show_student_by_grade(data)
        keys = ['student_id', 'name', 'tel', 'add', 'grade']

        return [dict(zip(keys, values)) for values in result]