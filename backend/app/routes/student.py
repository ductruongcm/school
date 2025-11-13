from flask import Blueprint
from app.utils import required_role, validate_input, with_log, ResponseBuilder
from flask_jwt_extended import jwt_required, get_jwt
from app.services import StudentServices, Student_Workflow, Academic_Student_Service
from app.schemas import StudentSchemas
from app.extensions import db
from app.repositories import Repositories


student_bp = Blueprint('student_bp', __name__, url_prefix = '/api')
student_service = StudentServices(db, Repositories)
academic_student_service = Academic_Student_Service(db, Repositories)
student_workflow = Student_Workflow(db, Repositories)

@student_bp.post('/students')
@jwt_required()
@required_role('admin', 'Teacher')
@with_log(True)
@validate_input(StudentSchemas.StudentCreate)
def add_student(validated_data):
    result = student_workflow.process_create_student(validated_data, get_jwt().get('id'))
    msg = f"Đã thêm học sinh {result['name']} vào hệ thống!"
    return ResponseBuilder.post(msg, result)
    
@student_bp.get('/years/<int:id>/students')
@jwt_required()
@required_role('admin')
@validate_input(StudentSchemas.StudentShowForAssignment)
def get_students_by_year(id, validated_data):
    validated_data['year_id'] = id
    result = academic_student_service.handle_show_students_for_class_assignment(validated_data)
    msg = f'Không còn học sinh chờ xếp lớp của khối!'
    return ResponseBuilder.get(msg, result)

@student_bp.get('/students')
@jwt_required()
@required_role('admin', 'Teacher')
@validate_input(StudentSchemas.StudentShow)
def show_students_route(validated_data):
    result = student_service.handle_show_students(validated_data)
    msg = 'Không tìm thấy thông tin tìm kiếm!'
    return ResponseBuilder.get(msg, result)

@student_bp.put('years/<int:id>/students/review')
@jwt_required()
@required_role('admin')
@validate_input(StudentSchemas.StudentReview)
def review_students(id, validated_data):
    student_workflow.process_review_students(validated_data, id, get_jwt().get('id'))
    msg = 'Đã xét duyệt học sinh!'
    return ResponseBuilder.put(msg)

@student_bp.post('/students/assignment')
@jwt_required()
@required_role('admin')
@validate_input(StudentSchemas.StudentAssignment)
def assign_student_for_new_year(validated_data):
    student_workflow.process_assign_students_for_new_year(validated_data, get_jwt().get('id'))
    msg = 'Đã hoàn thành xếp lớp cho học sinh!'
    return ResponseBuilder.post(msg)

@student_bp.put('/students')
@jwt_required()
@required_role('admin', 'Teacher')
@validate_input(StudentSchemas.StudentUpdate)
def update_students(validated_data):
    student_workflow.process_update_students(validated_data, get_jwt().get('id'))
    msg = 'Đã cập nhật thông tin học sinh!'
    return ResponseBuilder.put(msg)

@student_bp.get('years/<int:id>/students/summary')
@jwt_required()
@required_role('admin', 'Teacher')
@validate_input(StudentSchemas.StudentShowForScores)
def get_students_for_year_summary(id, validated_data):
    validated_data['year_id'] = id
    result = academic_student_service.handle_show_student_for_year_summary(validated_data)
    msg = 'Không tìm thấy thông tin!'
    return ResponseBuilder.get(msg, result)

@student_bp.get('semesters/<int:id>/students/summary')
@jwt_required()
@required_role('admin', 'Teacher')
@validate_input(StudentSchemas.StudentShowForScores)
def get_students_for_semester_summary(id, validated_data):
    validated_data['semester_id'] = id
    result = academic_student_service.handle_show_student_for_semester_summary(validated_data)
    msg = 'Không tìm thấy thông tin!'
    return ResponseBuilder.get(msg, result)


