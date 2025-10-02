from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.utils import required_role, error_show_return
from app.controllers import Monitoring_controller

monitoring_bp = Blueprint('monitoring_bp', __name__, url_prefix='/api/monitoring')

@monitoring_bp.get('/show_monitoring')
@jwt_required()
@required_role('admin')
def show_monitoring():
    result = Monitoring_controller.show_monitoring()
    errors = error_show_return(result)
    if errors:
        return errors

    return jsonify(result['data']), 200

