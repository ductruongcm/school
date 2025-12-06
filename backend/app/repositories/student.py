from .base import BaseRepo
from sqlalchemy import func, select
from app.models import Students, Student_info, Student_Year_Summary, Class_room

class StudentsRepo(BaseRepo):
    def get_student_by_student_code(self, data):
        return self.db.session.query(Students).filter(Students.student_code == data).first()
    
    def get_student_ids_by_year_and_class_room(self, data):
        return self.db.session.scalars(select(Students.id).join(Students.student_year_summary).filter(Student_Year_Summary.class_room_id == data['class_room_id'],
                                                                                                      Student_Year_Summary.year_id == data['year_id'])).all()

    def get_student_by_user(self, data: dict): 
        return self.db.session.query(Students).filter(Students.user_id == data['user_id']).scalar()

    def get_student_info_by_student(self, data: dict):
        return self.db.session.query(Student_info).filter(Student_info.student_id == data['student_id']).scalar()

    def get_student_by_id(self, data: dict):
        return self.db.session.query(Students).get(data['student_id'])
    
    def insert_student(self, data):
        student = Students(name = data['name'])
     
        student.student_info = [Student_info(tel = data['tel'],
                                            add = data['add'],
                                            gender = data['gender'],
                                            BOD = data['bod'])]
        self.db.session.add(student)
        self.db.session.flush()
        return student
    
    def student_last_code(self):
        #lấy cái student code lớn nhất
        #trả về next_num = 4 số cuối + 1, nếu ko có là 1 cho số đầu tiên
        last_code = self.db.session.query(func.max(Students.student_code)).scalar()
        if not last_code:
            next_num = 1
        else:
            last_num = int(last_code[-4:])
            next_num = last_num + 1
        return next_num
        
    def show_students_with_info(self, data):
        query = self.db.session.query(Students.id,
                                      Students.name,
                                      Student_info.gender,
                                      Student_info.BOD,
                                      Student_info.tel,
                                      Student_info.add,
                                      Student_Year_Summary.grade,
                                      Student_info.note,
                                      Student_Year_Summary.class_room_id).join(Students.student_info).join(Students.student_year_summary)
        if data.get('year_id'):
            query = query.filter(Student_Year_Summary.year_id == data['year_id'])

        if data.get('grade'):
            query = query.filter(Student_Year_Summary.grade == data['grade'])

        if data.get('class_room_id'):
            query = query.filter(Student_Year_Summary.class_room_id == data['class_room_id'])

        return query.all()
    
    def show_student_info_by_user(self, data: dict):
        return (self.db.session.query(Students.name,
                                      Students.student_code,
                                      Student_info.tel,
                                      Student_info.add,
                                      Class_room.class_room,
                                      Class_room.id,
                                      Class_room.grade,
                                      Student_Year_Summary.transfer_info)
                                            .join(Students.student_info)
                                            .join(Students.student_year_summary)
                                            .outerjoin(Class_room, Class_room.id == Student_Year_Summary.class_room_id)
                                                    .filter(Students.id == data['student_id'],
                                                            Student_Year_Summary.year_id == data['year_id']).all())
 

   