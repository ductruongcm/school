from app.schemas import ValidationError, AcademicShowSchemas, AcademicCreateSchemas
from app.extensions import db
from app.repositories import Class_room_repo, Academic_repo
from app.utils import error_422, error_400

class Class_room_service:
    @staticmethod
    def handle_add_class_room(data):
        try:
            class_room_data = AcademicCreateSchemas.ClassroomCreateSchema(**data)

        except ValidationError as e:
            return error_422(e)
        
        repo = Class_room_repo(class_room_data.year)
        if not repo:
            return error_400('Niên khóa không đúng!')
        
        elif repo.get_class_room(class_room_data.class_room):
            return error_400('Lớp học bị trùng!')
            
        try:
            repo.add_class_room(class_room_data.class_room)
            db.session.commit()
            return {'status': 'ok', 'msg': 'Addition class room success'}
        
        except Exception as e:
            db.session.rollback()
            return {'status': 'DB_error', 'msg': f'DB_error: {str(e)}'}
            
    @staticmethod
    def handle_show_class_room(data):
        try:
            show_data = AcademicShowSchemas.ClassroomShowSchema(**data)

        except ValidationError as e:
            return error_422(e)

        try:   
            repo = Class_room_repo(show_data.year)
            result = repo.show_class_room(show_data.class_room)
            if result:
                return {'status': 'ok', 'data': result}
            
            else:
                return error_400('Không tìm thấy thông tin')
        
        except Exception as e:
            return {'status': 'DB_error', 'msg': f'DB_error: {str(e)}'}
        
    @staticmethod
    def handle_show_teach_rooom(year, username):
        repo = Class_room_repo(year)
        if not repo:
            return error_400('Niên khóa không đúng!')

        try:
            result = Class_room_repo.show_teach_room(username)
            return {'status': 'ok', 'data': result}
        
        except Exception as e:
            return {'status': 'DB_error', 'msg': f'DB_error: {str(e)}'}
        
class Academic_service:
    @staticmethod
    def handle_add_year(data):
        try:
            add_year_data = AcademicCreateSchemas.YearCreateSchema(**data)

        except ValidationError as e:
            return error_422(e)   
        
        if Academic_repo.Get_repo.get_year(add_year_data.year):
                return error_400('Niên khóa bị trùng')
        
        try:
            Academic_repo.Add_repo.add_year(add_year_data.year)
            db.session.commit()
            return {'status': 'ok', 'msg': f'Thêm niên khóa thành công!'}

        except Exception as e:
            db.session.rollback()
            return {'status': 'DB_error', 'msg': f'DB_errror: {str(e)}'}
        

    @staticmethod
    def handle_add_semester(data):
        try:
            add_semester_data = AcademicCreateSchemas.SemesterCreateSchema(**data)

        except ValidationError as e:
            return error_422(e)
        
        if Academic_repo.Get_repo.get_semester(add_semester_data.semester):
            return error_400('Học kỳ bị trùng!')
        
        try:
            year_id = Academic_repo.Get_repo.get_year(add_semester_data.year).id
            Academic_repo.Add_repo.add_semester(add_semester_data.semester, year_id)
            db.session.commit()
            return {'status': 'ok', 'msg': f'Thêm học kỳ thành công!'}

        except Exception as e:
            db.session.rollback()
            return {'status': 'DB_error', 'msg': f'DB_errror: {str(e)}'}
    
    @staticmethod
    def handle_add_lesson(data):
        try:
            add_lesson_data = AcademicCreateSchemas.LessonCreateSchema(**data)

        except ValidationError as e:
            return error_422(e)
             
        if Academic_repo.Get_repo.get_lesson(add_lesson_data.lesson):
            return error_400('Môn học bị trùng')
        
        try:
            Academic_repo.Add_repo.add_lesson(add_lesson_data.lesson)
            db.session.commit()
            return {'status': 'ok', 'msg': 'Thêm lớp học thành công!'}
        
        except Exception as e:
            db.session.rollback()
            return {'status': 'DB_error', 'msg': f'DB_error: {str(e)}'}
        
    @staticmethod
    def handle_add_grade(data):
        try:
            add_grade_data = AcademicCreateSchemas.GradeCreateSchema(**data)
        
        except ValidationError as e:
            return error_422(e)
        
        if Academic_repo.Get_repo.get_grade(add_grade_data.grade):
            return error_400('Khối lớp bị trùng!')
        
        try:
            Academic_repo.Add_repo.add_grade(add_grade_data.grade)
            db.session.commit()
            return {'status': 'ok', 'msg': 'Thêm khối lớp thành công!'}

        except Exception as e:
            db.session.rollback()
            return {'static': 'DB_error', 'msg': f'{str(e)}'}    

    @staticmethod
    def handle_show_year(data):
        try:
            year_data = AcademicShowSchemas.YearShowSchema(**data)
        
        except ValidationError as e:
            return error_422(e)

        try:
            result = Academic_repo.Show_repo.show_year(year_data)
            if result:
                return {'status': 'ok', 'data': result}
            
            return error_400('Không tìm tháy thông tin!')
        
        except Exception as e:
            return {'static': 'DB_error', 'msg': f'{str(e)}'}    

    @staticmethod
    def handle_show_semester(data):
        try:
            semester_data = AcademicShowSchemas.SemesterShowSchema(**data)
        
        except ValidationError as e:
            return error_422(e)
        
        try:
            result = Academic_repo.Show_repo.show_semester(semester_data.semester)
            if not result:
                return error_400('Không tìm thấy thông tin!')
            
            return {'status': 'ok', 'data': result}
        
        except Exception as e:
            return {'static': 'DB_error', 'msg': f'{str(e)}'}  

    @staticmethod
    def handle_show_lesson(data):
        try:
            lesson_data = AcademicShowSchemas.LessonShowSchema(**data)

        except ValidationError as e:
            return error_422(e)
        
        try:
            result = Academic_repo.Show_repo.show_lesson(lesson_data.lesson)
            if result:
                return {'status': 'ok', 'data': result}
            
            return error_400('Không tìm tháy thông tin!')
        
        except Exception as e:
            return {'status': 'DB_error', 'msg': f'DB_error: {str(e)}'}
        
    @staticmethod
    def handle_show_grade(data):
        try:
            grade_data = AcademicShowSchemas.GradeShowSchema(**data)

        except ValidationError as e:
            return error_422(e)
        
        try:
            result = Academic_repo.Show_repo.show_grade(grade_data.grade)
            if result:
                return {'status': 'ok', 'data': result}
            
            else:
                error_400('Không tìm thấy thông tin!')

        except Exception as e:
            return {'status': 'DB_error', 'msg': f'DB_error: {str(e)}'}