from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.utils import required_role, validate_input, ResponseBuilder
from app.extensions import db
from app.repositories import AuditLogRepo, Repositories
from app.services import AuditLog_Service, ActivityLog_Service
from app.schemas import AuditShowSchema, ActivityShowSchema


log_bp = Blueprint('log_bp', __name__, url_prefix='/api')
audit_service = AuditLog_Service(db, AuditLogRepo)
activity_log_service = ActivityLog_Service(db, Repositories)

@log_bp.get('/audit')
@jwt_required()
@required_role('admin')
@validate_input(AuditShowSchema)
def show_monitoring(validated_data):
    result = audit_service.handle_show_logs(validated_data)
    msg = 'Thông tin tìm kiếm không có!'
    return ResponseBuilder.get(msg, result)

@log_bp.get('/activity-log')
@jwt_required()
@required_role('admin', 'Teacher')
@validate_input(ActivityShowSchema)
def show_activity_log(validated_data):
    validated_data.update({'role': get_jwt().get('role')})
    result = activity_log_service.handle_show_activity_logs(validated_data , get_jwt_identity())
    msg = 'Thông tin tìm kiếm không có!'
    return ResponseBuilder.get(msg, result)