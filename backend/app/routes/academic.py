from flask import Blueprint
from app.utils import required_role, validate_input, ResponseBuilder, with_log
from flask_jwt_extended import jwt_required, get_jwt
from app.schemas import AcademicShowSchemas, AcademicSchemas
from app.services import AcademicAddService, AcademicShowService, AcademicUpdateService
from app.extensions import db
from app.repositories import AcademicAddRepo, AcademicGetRepo, AcademicShowRepo, AcademicUpdateRepo, AcademicCheckRepo

academic_bp = Blueprint('academic_bp', __name__, url_prefix = '/api/academic')
academic_add = AcademicAddService(db, AcademicGetRepo, AcademicAddRepo, AcademicCheckRepo)
academic_show = AcademicShowService(db, AcademicShowRepo)
academic_update = AcademicUpdateService(db, AcademicGetRepo, AcademicUpdateRepo, AcademicCheckRepo)

@academic_bp.post('/years')
@jwt_required()
@required_role('admin')
@validate_input(AcademicSchemas.Year)
def add_year_route(validated_data):
    result = academic_add.handle_add_year(validated_data)    
    msg = f"Đã thêm niên khóa {result['data']}!"
    return ResponseBuilder.post(msg)

@academic_bp.get('/years')
@validate_input(AcademicShowSchemas.YearShow)
def show_year_route(validated_data):
    result = academic_show.handle_show_year(validated_data)
    msg = 'Không tìm thấy dữ liệu!'   
    return ResponseBuilder.get(msg, result)

@academic_bp.put('/years/<int:id>')
def set_year_route(id):
    result = academic_update.handle_set_year({'year_id': id})
    msg = f"Đã thiết lập niên khóa {result.year}"
    return ResponseBuilder.put(msg, {'id': result.id, 'year': result.year})

@academic_bp.post('/semesters')
@jwt_required()
@required_role('admin')
@validate_input(AcademicSchemas.Semester)
def add_semester_route(validated_data):
    result = academic_add.handle_add_semester(validated_data)
    msg = f"Đã thêm học kỳ {result['data']}!"
    return ResponseBuilder.post(msg)

@academic_bp.get('/semesters')
@jwt_required()
@required_role('admin')
@validate_input(AcademicShowSchemas.SemesterShow)
def show_semester_route(validated_data):
    result = academic_show.handle_show_semester(validated_data)
    msg = 'Không tìm thấy dữ liệu!'   
    return ResponseBuilder.get(msg, result)

@academic_bp.post('/grades')
@jwt_required()
@required_role('admin')
@validate_input(AcademicSchemas.Grade)
def add_grade_route(validated_data):
    result = academic_add.handle_add_grade(validated_data)
    msg = f"Đã thêm khối lớp {result['data']}!"
    return ResponseBuilder.post(msg)

@academic_bp.get('/grades')
@jwt_required()
@required_role('admin')
@validate_input(AcademicShowSchemas.GradeShow)
def show_grade_route(validated_data):
    result = academic_show.handle_show_grade(validated_data)
    msg = 'Không tìm thấy dữ liệu!'   
    return ResponseBuilder.get(msg, result)

@academic_bp.post('/lessons')
@jwt_required()
@required_role('admin')
@validate_input(AcademicSchemas.Lesson)
def add_lesson_route(validated_data):
    result = academic_add.handle_add_lesson(validated_data)
    msg = f"Đã thêm môn học {result['data']}!"
    return ResponseBuilder.post(msg)

@academic_bp.get('/lessons')
@jwt_required()
@required_role('admin', 'teacher')
@validate_input(AcademicShowSchemas.LessonShow)
def show_lesson_route(validated_data):
    validated_data['role'] = get_jwt().get('role')
    result = academic_show.handle_show_lesson(validated_data)
    msg = 'Không tìm thấy dữ liệu!'   
    return ResponseBuilder.get(msg, result)

@academic_bp.put('/lessons')
@jwt_required()
@required_role('admin')
@validate_input(AcademicSchemas.LessonUpdate)
def update_lesson_route(validated_data):
    result = academic_update.handle_update_lesson(validated_data)
    msg = f"Đã cập nhật danh sách môn học {result['lesson']}"
    return ResponseBuilder.put(msg)

@academic_bp.post('/class_rooms')
@jwt_required()
@required_role('admin')
@validate_input(AcademicSchemas.Classroom)
def add_class_room_route(validated_data):
    result = academic_add.handle_add_class_room(validated_data)
    msg = f"Đã thêm lớp {result['data']}!"
    return ResponseBuilder.post(msg)
    
@academic_bp.get('/class_rooms')
@jwt_required()
@required_role('admin', 'teacher')
@validate_input(AcademicShowSchemas.ClassroomShow)
def class_room_show(validated_data):
    result = academic_show.handle_show_class_room(validated_data)
    msg = 'Không tìm thấy dữ liệu!'   
    return ResponseBuilder.get(msg, result)

@academic_bp.put('/class_rooms')
@jwt_required()
@required_role('admin')
@validate_input(AcademicSchemas.ClassUpdate)
def update_class_room_route(validated_data):
    result = academic_update.handle_update_class_room(validated_data)
    msg = f"Đã cập nhật lại các lớp {result['class_room']}"
    return ResponseBuilder.put(msg)

# @academic_bp.post('/class_lesson')
# @jwt_required()
# @required_role('admin')
# @validate_input(AcademicCreateSchemas.ClassLesson)
# def assign_class_lesson(validated_data):
#     result = academic_add.handle_assign_class_lesson(validated_data)
#     return jsonify({'msg': result['msg']}), 201

@academic_bp.get('/teach_classes')
@jwt_required()
@required_role('teacher', 'admin')
@validate_input(AcademicShowSchemas.ClassroomShow)
def teach_room_show(validated_data):
    validated_data['role'] = get_jwt().get('role')
    result = academic_show.handle_show_teach_room(validated_data)
    msg = 'Không tìm thấy dữ liệu!'   
    return ResponseBuilder.get(msg, result)

@academic_bp.get('/teach_classes/<int:lesson_id>')
@jwt_required()
@required_role('admin')
@validate_input(AcademicShowSchemas.TeachLessClass)
def teach_class_by_lesson_id(lesson_id: int, validated_data):
    validated_data['lesson_id'] = lesson_id
    result = academic_show.handle_show_teach_class_with_teacher_id_by_lesson_id(validated_data)
    msg = 'Không tìm thấy dữ liệu!'   
    return ResponseBuilder.get(msg, result)

@academic_bp.put('/class_rooms/<int:id>/students')
@jwt_required()
@required_role('admin')
@validate_input(AcademicSchemas.AssignStudent)
def assign_student(id, validated_data):
    validated_data['class_room_id'] = id
    result = academic_update.handle_assign_student_to_class(validated_data)
    msg = f'Đã thêm học sinh được chọn vào lớp {result['class_room']}!'
    return ResponseBuilder.put(msg)

@academic_bp.put('/semester')
@jwt_required()
@required_role('admin')
@validate_input(AcademicSchemas.SemesterUpdate)
def update_semester_route(validated_data):
    result = academic_update.handle_update_semester(validated_data)
    msg = f'Đã cập  nhật học kỳ {result['semester']}'
    return ResponseBuilder.put(msg)

@academic_bp.post('/scores')
@jwt_required()
@required_role('admin')
@validate_input(AcademicSchemas.Scores)
def create_scores_route(validated_data):
    result = academic_add.handle_add_scores(validated_data)
    msg = f'Đã tạo bảng điểm cho {result['semester']}'
    return ResponseBuilder.post(msg)

@academic_bp.post('/schedules')
@jwt_required()
@required_role('admin')
@validate_input(AcademicSchemas.Schedule)
def create_schedule_route(validated_data):
    result = academic_add.handle_add_schedule(validated_data)
    msg = f"Đã thêm thời khóa biểu của lớp {result['data']}!"
    return ResponseBuilder.post(msg)
