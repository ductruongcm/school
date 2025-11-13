from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt
from app.utils import required_role, validate_input, with_log, ResponseBuilder
from app.extensions import db
from app.schemas import TeacherSchemas
from app.services import TeacherService, Teacher_Workflow
from app.repositories import Repositories

teacher_bp = Blueprint('teacher_bp', __name__, url_prefix='/api')
teacher_service = TeacherService(db, Repositories)
teacher_workflow = Teacher_Workflow(db, Repositories)

@teacher_bp.post('/teachers')
@jwt_required()
@required_role('admin')
@with_log(True)
@validate_input(TeacherSchemas.TeacherCreateSchema)
def add_teacher(validated_data):
    result = teacher_workflow.process_create_teacher(validated_data)
    msg = f'Đã thêm giáo viên {result['name']}!'
    return ResponseBuilder.post(msg)
  
@teacher_bp.get('me/teachers')
@jwt_required()
@required_role('admin', 'Teacher')
@validate_input(TeacherSchemas.TeacherShowSchema)
def show_teacher(validated_data):
    validated_data.update({'role': get_jwt().get('role')})
    result = teacher_service.handle_show_teachers(validated_data)
    msg = 'Thông tin tìm kiếm không có!'
    return ResponseBuilder.get(msg, result)

@teacher_bp.put('/teachers/<int:id>')
@jwt_required()
@required_role('admin')
@with_log(True)
@validate_input(TeacherSchemas.TeacherUpdateSchema)
def update_info(id: int, validated_data):
    validated_data['teacher_id'] = id
    result = teacher_workflow.process_update_teacher(validated_data)
    if result:
        msg = f'Đã cập nhật lại thông tin của giáo viên {result.name}!'
    else:
        msg = 'Không có cập nhật gì!'
    return ResponseBuilder.put(msg)

@teacher_bp.put('/teachers/<int:id>/status')
@jwt_required()
@required_role('admin')
def set_status_teacher(id: int):
    result = teacher_service.handle_status_teacher({'teacher_id': id})
    msg = f'Đã ẩn giáo viên {result.name}!' if not result.status else f'Đã hiện giáo viên {result.name}!'
    return ResponseBuilder.put(msg)

@teacher_bp.delete('/teachers/<int:id>')
@jwt_required()
@required_role('admin')
def delete_teacher(id: int, validated_data):
    validated_data['teacher_id'] = id
    result = teacher_service.handle_delete_teacher(validated_data)
    return result

