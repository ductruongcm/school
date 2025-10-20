from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.utils import required_role, validate_input, ResponseBuilder
from app.extensions import db
from app.repositories import AuditRepo
from app.services import AuditService
from app.schemas import AuditShowSchema


audit_bp = Blueprint('audit_bp', __name__, url_prefix='/api')
audit_service = AuditService(db, AuditRepo)

@audit_bp.get('/audit')
@jwt_required()
@required_role('admin')
@validate_input(AuditShowSchema)
def show_monitoring(validated_data):
    result = audit_service.handle_show_logs(validated_data)
    msg = 'Thông tin tìm kiếm không có!'
    return ResponseBuilder.get(msg, result)

