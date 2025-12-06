from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.utils import required_role, ResponseBuilder, validate_input
from app.extensions import db
from app.repositories import Repositories
from app.schemas import AcademicShowSchemas
from app.services import Dashboard_Service

dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='/api/dashboard')
dashboard_service = Dashboard_Service(db, Repositories)

@dashboard_bp.get('/years/<int:id>/class-rooms')
@jwt_required()
@required_role('admin')
@validate_input(AcademicShowSchemas.SemesterId)
def show_class_rooms_info(id, validated_data):
    validated_data['year_id'] = id
    result = dashboard_service.handle_show_class_room_infos_by_year(validated_data)    
    msg = 'Không tìm thấy thông tin!'
    return ResponseBuilder.get(msg, result)

@dashboard_bp.get('/years/<int:id>/summary')
@jwt_required()
@required_role('admin')
@validate_input(AcademicShowSchemas.SemesterId)
def show_summary(id, validated_data):
    validated_data['year_id'] = id
    result = dashboard_service.handle_show_summary_info_by_year(validated_data)
    msg = 'Không tìm thấy thông tin!'
    return ResponseBuilder.get(msg, result)