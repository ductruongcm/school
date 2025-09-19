from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.utils.role_utils import required_role
from app.db_utils.db_monitoring_utils import db_show_monitoring

monitoring_bp = Blueprint('monitoring_bp', __name__, url_prefix='/api/monitoring')

@monitoring_bp.get('/show_monitoring')
@jwt_required()
@required_role('admin')
def show_monitoring():
    ip = request.args.get('ip')
    username = request.args.get('username')
    action = request.args.get('action')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    status = request.args.get('status')
    info = request.args.get('info')

    data = db_show_monitoring(ip, username, action, start_date, end_date, status, info)

    return jsonify({'data': data}), 200