from app.schemas import ValidationError, AcademicShowSchemas, AcademicCreateSchemas
from app.extensions import db
from app.repositories import ClassroomsRepositories, AcademicRepositories
from app.utils import error_422, error_400
import traceback

class ClassroomService:
    @staticmethod
    def handle_add_class_room(data):
        try:
            class_room_data = AcademicCreateSchemas.ClassroomCreateSchema(**data)

        except ValidationError as e:
            return error_422(e)
        
        repo = ClassroomsRepositories(class_room_data.year)
        if not repo:
            return error_400('Niên khóa không đúng!')
        
        elif repo.get_class_room(class_room_data.class_room):
            return error_400('Lớp học bị trùng!')
            
        try:
            repo.add_class_room(class_room_data.class_room)
            db.session.commit()
            return {'status': 'ok', 'msg': 'Addition class room success'}
        
        except Exception as e:
            print('trace', traceback.format_exc())
            db.session.rollback()
            return {'status': 'DB_error', 'msg': f'DB_error: {str(e)}'}
            
    @staticmethod
    def handle_show_class_room(data):
        try:
            show_data = AcademicShowSchemas.ClassroomShowSchema(**data)

        except ValidationError as e:
            return error_422(e)

        try:   
            repo = ClassroomsRepositories(show_data.year)
            result = repo.show_class_room(show_data.class_room)
            keys = ['class_room_id', 'class_room']

            if result:
                return {'status': 'ok', 'data': [dict(zip(keys, values)) for values in result]}
            
            else:
                return error_400('Không tìm thấy thông tin')
        
        except Exception as e:
            print('trace', traceback.format_exc())
            return {'status': 'DB_error', 'msg': f'DB_error: {str(e)}'}
        
    @staticmethod
    def handle_show_teach_room(year, role, id):
        repo = ClassroomsRepositories(year)
        if not repo:
            return error_400('Niên khóa không đúng!')

        try:
            if role == 'admin':
                result = repo.show_class_room()
                
            elif role == 'teacher':
                result = ClassroomsRepositories.show_teach_room(id)

            keys = ['class_room_id', 'class_room']
            return {'status': 'success', 'data': [dict(zip(keys, values)) for values in result]}
        
        except Exception as e:
            print('trace', traceback.format_exc())
            return {'status': 'DB_error', 'msg': f'DB_error: {str(e)}'}
        
class AcademicService:
    @staticmethod
    def handle_add_year(data):
        try:
            add_year_data = AcademicCreateSchemas.YearCreateSchema(**data)

        except ValidationError as e:
            return error_422(e)   
        
        if AcademicRepositories.Get_repo.get_year(add_year_data.year):
                return error_400('Niên khóa bị trùng')
        
        try:
            AcademicRepositories.Add_repo.add_year(add_year_data.year)
            db.session.commit()
            return {'status': 'ok', 'msg': f'Thêm niên khóa thành công!'}

        except Exception as e:
            print('trace', traceback.format_exc())
            db.session.rollback()
            return {'status': 'DB_error', 'msg': f'DB_errror: {str(e)}'}
        
    @staticmethod
    def handle_add_semester(data):
        try:
            add_semester_data = AcademicCreateSchemas.SemesterCreateSchema(**data)

        except ValidationError as e:
            return error_422(e)
        
        if AcademicRepositories.Get_repo.get_semester(add_semester_data.semester):
            return error_400('Học kỳ bị trùng!')
        
        try:
            year_id = AcademicRepositories.Get_repo.get_year(add_semester_data.year).id
            AcademicRepositories.Add_repo.add_semester(add_semester_data.semester, year_id)
            db.session.commit()
            return {'status': 'ok', 'msg': f'Thêm học kỳ thành công!'}

        except Exception as e:
            print('trace', traceback.format_exc())
            db.session.rollback()
            return {'status': 'DB_error', 'msg': f'DB_errror: {str(e)}'}
    
    @staticmethod
    def handle_add_lesson(data):
        try:
            add_lesson_data = AcademicCreateSchemas.LessonCreateSchema(**data)

        except ValidationError as e:
            return error_422(e)
             
        if AcademicRepositories.Get_repo.get_lesson(add_lesson_data.lesson):
            return error_400('Môn học bị trùng')
        
        try:
            AcademicRepositories.Add_repo.add_lesson(add_lesson_data.lesson)
            db.session.commit()
            return {'status': 'ok', 'msg': 'Thêm lớp học thành công!'}
        
        except Exception as e:
            print('trace', traceback.format_exc())
            db.session.rollback()
            return {'status': 'DB_error', 'msg': f'DB_error: {str(e)}'}
        
    @staticmethod
    def handle_add_grade(data):
        try:
            add_grade_data = AcademicCreateSchemas.GradeCreateSchema(**data)
        
        except ValidationError as e:
            return error_422(e)
        
        if AcademicRepositories.Get_repo.get_grade(add_grade_data.grade):
            return error_400('Khối lớp bị trùng!')
        
        try:
            AcademicRepositories.Add_repo.add_grade(add_grade_data.grade)
            db.session.commit()
            return {'status': 'ok', 'msg': 'Thêm khối lớp thành công!'}

        except Exception as e:
            print('trace', traceback.format_exc())
            db.session.rollback()
            return {'static': 'DB_error', 'msg': f'{str(e)}'}    

    @staticmethod
    def handle_show_year(data):
        try:
            year_data = AcademicShowSchemas.YearShowSchema(**data)
        
        except ValidationError as e:
            return error_422(e)

        try:
            result = AcademicRepositories.Show_repo.show_year(year_data)
            if result:
                return {'status': 'ok', 'data': result}
            
            return error_400('Không tìm tháy thông tin!')
        
        except Exception as e:
            print('trace', traceback.format_exc())
            return {'static': 'DB_error', 'msg': f'{str(e)}'}    

    @staticmethod
    def handle_show_semester(data):
        try:
            semester_data = AcademicShowSchemas.SemesterShowSchema(**data)
        
        except ValidationError as e:
            return error_422(e)
        
        try:
            result = AcademicRepositories.Show_repo.show_semester(semester_data.semester)
            if not result:
                return error_400('Không tìm thấy thông tin!')
            
            return {'status': 'ok', 'data': result}
        
        except Exception as e:
            print('trace', traceback.format_exc())
            return {'static': 'DB_error', 'msg': f'{str(e)}'}  

    @staticmethod
    def handle_show_lesson(data, role, id):
        try:
            lesson_data = AcademicShowSchemas.LessonShowSchema(**data)

        except ValidationError as e:
            return error_422(e)
        
        try:
            if role == 'admin':
                keys = ['lesson_id', 'lesson']
                result = AcademicRepositories.Show_repo.show_lesson()
                return {'status': 'Success', 'data': [dict(zip(keys, values)) for values in result]}
            
            # elif role == 'teacher':
            #     keys = ['lesson_id', 'lesson', 'teacher_id', 'class_room_id']
            #     result = AcademicRepositories.Show_repo.show_lesson_by_id(id, lesson_data.class_room)
            #     return {'status': 'Success', 'data': [dict(zip(keys, values)) for values in result]}

            return error_400('Không tìm thấy thông tin!')
      
        except Exception as e:
            print('trace', traceback.format_exc())
            return {'status': 'DB_error', 'msg': f'DB_error: {str(e)}'}
        
    @staticmethod
    def handle_show_grade(data):
        try:
            grade_data = AcademicShowSchemas.GradeShowSchema(**data)

        except ValidationError as e:
            return error_422(e)
        
        try:
            result = AcademicRepositories.Show_repo.show_grade(grade_data.grade)
            if result:
                return {'status': 'ok', 'data': result}
            
            else:
                error_400('Không tìm thấy thông tin!')

        except Exception as e:
            print('trace', traceback.format_exc())
            return {'status': 'DB_error', 'msg': f'DB_error: {str(e)}'}