from flask import Blueprint
from app.utils import required_role, validate_input, ResponseBuilder, with_log
from flask_jwt_extended import jwt_required, get_jwt
from app.schemas import AcademicSchemas
from app.services import Academic_Relation_Service
from app.extensions import db
from app.repositories import Repositories

academic_relation_bp = Blueprint('academic_relation_bp', __name__, url_prefix = '/api/academic/relation')
academic_relation_service = Academic_Relation_Service(db, Repositories)

@academic_relation_bp.post('/lessons-class')
@jwt_required()
@required_role('admin')
# @with_log(True)
@validate_input(AcademicSchemas.Lessons_Class)
def create_lessons_class(validated_data):
    academic_relation_service.handle_link_lesson_class_by_year(validated_data, get_jwt().get('id'))
    msg = 'Đã tạo dữ liệu cho bảng môn học và lớp!'
    return ResponseBuilder.post(msg)





