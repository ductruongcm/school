from flask import Blueprint
from app.utils import required_role, validate_input, ResponseBuilder
from flask_jwt_extended import jwt_required, get_jwt
from app.schemas import AcademicShowSchemas, AcademicSchemas, AcademicUpdateSchemas
from app.services import AcademicAddService, AcademicShowService, AcademicUpdateService, Academic_Relation_Workflow
from app.extensions import db
from app.repositories import Repositories

academic_bp = Blueprint('academic_bp', __name__, url_prefix = '/api/academic')
academic_add_service= AcademicAddService(db, Repositories)
academic_show_service = AcademicShowService(db, Repositories)
academic_update_service = AcademicUpdateService(db, Repositories)
academic_relation_workflow = Academic_Relation_Workflow(db, Repositories)

#year
@academic_bp.post('/years')
@jwt_required()
@required_role('admin')
@validate_input(AcademicSchemas.Year)
def add_year_route(validated_data):
    result = academic_add_service.handle_add_year(validated_data)    
    msg = f"Đã thêm niên khóa {result['year_code']}!"
    return ResponseBuilder.post(msg)

@academic_bp.get('/years')
@validate_input(AcademicShowSchemas.YearShow)
def show_year_route(validated_data):
    result = academic_show_service.handle_show_year(validated_data)
    msg = 'Không tìm thấy dữ liệu!'   
    return ResponseBuilder.get(msg, result)

@academic_bp.get('/me/years')
@jwt_required()
@validate_input(AcademicShowSchemas.YearShow)
def show_my_year_route(validated_data):
    validated_data.update({'role': get_jwt().get('role'),
                           'user_id': get_jwt().get('user_id')})
    
    result = academic_show_service.handle_show_year(validated_data)
    msg = 'Không tìm thấy dữ liệu!'   
    return ResponseBuilder.get(msg, result)

@academic_bp.put('/years/<int:id>/status')
def set_year_route(id):
    result = academic_update_service.handle_set_year({'year_id': id})
    msg = f"Đã thiết lập niên khóa {result.year_code}"
    return ResponseBuilder.put(msg, {'id': result.id, 'year': result.year_code})

#semester
@academic_bp.post('/semesters')
@jwt_required()
@required_role('admin')
@validate_input(AcademicSchemas.Semester)
def add_semester_route(validated_data):
    result = academic_add_service.handle_add_semester(validated_data)
    msg = f"Đã thêm học kỳ {result['data']}!"
    return ResponseBuilder.post(msg)

@academic_bp.get('/semesters')
@validate_input(AcademicShowSchemas.SemesterShow)
def show_semester_route(validated_data):
    result = academic_show_service.handle_show_semester(validated_data)
    msg = 'Không tìm thấy dữ liệu!'   
    return ResponseBuilder.get(msg, result)

@academic_bp.put('/semesters')
@jwt_required()
@required_role('admin')
@validate_input(AcademicSchemas.SemesterUpdate)
def update_semester_route(validated_data):
    result = academic_update_service.handle_update_semester(validated_data)
    msg = f'Đã cập  nhật học kỳ {result['semester']}'
    return ResponseBuilder.put(msg)

@academic_bp.put('/semesters/<int:id>/status')
@jwt_required()
@required_role('admin')
def set_semester_status_route(id):
    result = academic_update_service.handle_set_semester({'semester_id': id})
    msg = f'Đã thiết lập học kỳ {result.semester}!'
    return ResponseBuilder.put(msg)

#grades
@academic_bp.post('/grades')
@jwt_required()
@required_role('admin')
@validate_input(AcademicSchemas.Grade)
def add_grade_route(validated_data):
    result = academic_add_service.handle_add_grade(validated_data, get_jwt().get('id'))
    msg = f"Đã thêm khối lớp {result['data']}!"
    return ResponseBuilder.post(msg)

@academic_bp.get('/grades')
@jwt_required()
@required_role('admin', 'Teacher')
@validate_input(AcademicShowSchemas.GradeShow)
def show_grade_route(validated_data):
    result = academic_show_service.handle_show_grade(validated_data)
    msg = 'Không tìm thấy dữ liệu!'   
    return ResponseBuilder.get(msg, result)

@academic_bp.put('/grades')
@jwt_required()
@required_role('admin')
@validate_input(AcademicUpdateSchemas.Grade)
def update_grade(validated_data):
    academic_update_service.handle_update_grades(validated_data, get_jwt().get('id'))
    msg = 'Đã cập nhật lại thông tin khối lớp!'
    return ResponseBuilder.put(msg)

#lessons
@academic_bp.post('/lessons')
@jwt_required()
@required_role('admin')
@validate_input(AcademicSchemas.Lesson)
def add_lesson_route(validated_data):
    result = academic_add_service.handle_add_lesson(validated_data, get_jwt().get('id'))
    msg = f"Đã thêm môn học {result.lesson}!"
    return ResponseBuilder.post(msg)

@academic_bp.get('/me/lessons')
@jwt_required()
@required_role('admin', 'Teacher', 'Student')
@validate_input(AcademicShowSchemas.LessonShow)
def show_lesson_route(validated_data):
    validated_data.update({'role': get_jwt().get('role'),
                           'user_id': get_jwt().get('id')})
    result = academic_show_service.handle_show_lessons(validated_data)
    msg = 'Không tìm thấy dữ liệu!'   
    return ResponseBuilder.get(msg, result)

@academic_bp.put('/lessons')
@jwt_required()
@required_role('admin')
@validate_input(AcademicSchemas.LessonUpdate)
def update_lesson_route(validated_data):
    academic_relation_workflow.process_update_lesson(validated_data, get_jwt().get('id'))
    msg = f"Đã cập nhật danh sách môn học!"
    return ResponseBuilder.put(msg)

@academic_bp.get('/grades/<int:grade>/lessons')
@jwt_required()
@required_role('admin', 'Teacher')
def show_lessons_by_grade_route(grade):
    validated_data = {'grade': grade}
    result = academic_show_service.handle_show_lessons_by_grade(validated_data)
    msg = 'Không tìm thấy thông tin dữ liệu!'
    return ResponseBuilder.get(msg, result)

#class_room
@academic_bp.post('/class-rooms')
@jwt_required()
@required_role('admin')
@validate_input(AcademicSchemas.Classroom)
def add_class_room_route(validated_data):
    result = academic_add_service.handle_add_class_room(validated_data)
    msg = f"Đã thêm lớp {result['data']}!"
    return ResponseBuilder.post(msg)

@academic_bp.put('/class-rooms')
@jwt_required()
@required_role('admin')
@validate_input(AcademicSchemas.ClassUpdate)
def update_class_room_route(validated_data):
    result = academic_update_service.handle_update_class_room(validated_data)
    msg = f"Đã cập nhật lại các lớp {result['class_room']}"
    return ResponseBuilder.put(msg)

@academic_bp.get('/years/<int:id>/class-rooms/assignable')
@jwt_required()
@required_role('admin')
@validate_input(AcademicShowSchemas.ClassRoomShowForAssignment)
def show_class_for_assignment(id, validated_data):
    validated_data['year_id'] = id
    result = academic_show_service.handle_show_class_room_for_assignment(validated_data)
    msg = 'Không tìm thấy dữ liệu!'   
    return ResponseBuilder.get(msg, result)

@academic_bp.get('/years/<int:id>/me/class-rooms')
@jwt_required()
@required_role('admin', 'Teacher', 'Student')
@validate_input(AcademicShowSchemas.ClassroomShow)
def class_room_show(id, validated_data): 
    validated_data.update({'user_id': get_jwt().get('id'),
                           'role': get_jwt().get('role'),
                           'year_id': id})  
    result = academic_relation_workflow.process_show_class_room(validated_data)
    msg = 'Không tìm thấy dữ liệu!'   
    return ResponseBuilder.get(msg, result)

@academic_bp.get('/lessons/<int:lesson_id>/class-rooms')
@jwt_required()
@required_role('admin')
@validate_input(AcademicShowSchemas.TeachLessClass)
def teach_class_by_lesson_id(lesson_id: int, validated_data):
    #lấy lớp theo môn
    validated_data['lesson_id'] = lesson_id
    result = academic_show_service.handle_show_teach_class_with_teacher_id_by_lesson_id(validated_data)
    msg = 'Không tìm thấy dữ liệu!'   
    return ResponseBuilder.get(msg, result)

@academic_bp.post('/score-types')
@jwt_required()
@required_role('admin')
@validate_input(AcademicSchemas.ScoreTypes)
def create_score_types(validated_data):
    academic_add_service.handle_add_score_types(validated_data, get_jwt().get('id'))
    msg = 'Đã tạo loại điểm số!'
    return ResponseBuilder.post(msg)

@academic_bp.get('/score-types')
@jwt_required()
@required_role('admin')
def show_score_types():
    result = academic_show_service.handle_show_score_types()
    msg = 'Không tìm thấy dữ liệu!'   
    return ResponseBuilder.get(msg, result)

@academic_bp.put('/score-types')
@jwt_required()
@required_role('admin')
@validate_input(AcademicUpdateSchemas.ScoreTypes)
def update_score_types(validated_data):
    academic_update_service.handle_update_score_types(validated_data, get_jwt().get('id'))
    msg = f"Đã cập nhật lại điểm số!"
    return ResponseBuilder.put(msg)




