from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.utils import required_role, ResponseBuilder, validate_input
from app.extensions import db
from app.repositories import Repositories
from app.schemas import AcademicShowSchemas
from app.services import Dashboard_Service

report_bp = Blueprint('report_bp', __name__, url_prefix='/api/report')
report_service = Dashboard_Service(db, Repositories)

@report_bp.get('/daily/class-rooms')
@jwt_required()
@required_role('admin')
@validate_input(AcademicShowSchemas.ClassInfoForDashboard)
def show_class_rooms_info(validated_data):
    result = report_service.handle_show_daily_class_room_infos(validated_data)    
    msg = 'Không tìm thấy thông tin!'
    return ResponseBuilder.get(msg, result)

@report_bp.get('/years/<int:id>/info')
@jwt_required()
@required_role('admin')
@validate_input(AcademicShowSchemas.SemesterId)
def show_summary(id, validated_data):
    validated_data['year_id'] = id
    result = report_service.handle_show_summary_info_by_year(validated_data)
    msg = 'Không tìm thấy thông tin!'
    return ResponseBuilder.get(msg, result)

@report_bp.get('/years/<int:id>/summary/report')
@jwt_required()
@required_role('admin')
def show_report_year_summary(id):
    result = report_service.handle_show_year_summary_result(id)
    msg = 'Không tìm thấy thông tin!'
    return ResponseBuilder.get(msg, result)