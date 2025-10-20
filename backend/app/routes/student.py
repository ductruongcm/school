from flask import Blueprint
from app.utils import required_role, validate_input, with_log, ResponseBuilder
from flask_jwt_extended import jwt_required
from app.services import StudentServices
from app.schemas import StudentSchemas
from app.extensions import db
from app.repositories import StudentsRepo, AcademicGetRepo


student_bp = Blueprint('student_bp', __name__, url_prefix = '/api')
student_service = StudentServices(db, StudentsRepo, AcademicGetRepo)

@student_bp.post('/students')
@jwt_required()
@required_role('admin', 'Teacher')
@with_log(True)
@validate_input(StudentSchemas.StudentCreate)
def add_student(validated_data):
    result = student_service.handle_add_student(validated_data)
    msg = f"Đã thêm học sinh {result['name']} vào lớp {result['class_room']}" if result['class_room'] else f"Đã thêm học sinh {result['name']}" 
    return ResponseBuilder.post(msg, result)

@student_bp.get('/students')
@jwt_required()
@required_role('admin', 'Teacher')
@validate_input(StudentSchemas.StudentShow)
def show_students_by_grade_route(validated_data):
    result = student_service.handle_show_student_by_grade(validated_data)
    msg = 'Không tìm thấy thông tin tìm kiếm!'
    return ResponseBuilder.get(msg, result)

# @student_bp.get('/show_student')
# @jwt_required()
# @required_role('admin', 'teacher')
# def show_student():
#     class_room = request.args.get('class_room')
#     data = db_show_student(class_room)
#     return jsonify({'data': data}), 200
    
# @student_bp.put('/update_info')
# @jwt_required()
# @required_role('admin')
# def update_info():
#     username = get_jwt_identity()
#     student_id = request.get_json().get('id')
#     name = request.get_json().get('name')
#     tel = request.get_json().get('tel')
#     add = request.get_json().get('add')
#     errors = validators.errors(name = name, tel = tel, add = add)
#     if errors:
#         AuditService.handle_add_monitoring(username, 'update student info', 'FAIL', f'Update {name}: {errors}')
#         return jsonify({'msg': errors}), 400
    
#     db_update_info(student_id, name, tel, add)
#     AuditService.handle_add_monitoring(username, 'update student info', 'SUCCESS', f'Update: {name}')
#     return jsonify({'msg': 'Updated!'}), 200

# @student_bp.get('/show_score')
# @jwt_required()
# @required_role('admin', 'teacher')
# def show_score():
#     class_room = request.args.get('class_room')
#     lesson = request.args.get('lesson')
#     data = db_show_score(class_room, lesson)
#     return jsonify({'data': data})