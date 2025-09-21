from flask import Blueprint, request, jsonify
from app.utils import role_utils, utils
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.db_utils.db_class_room_utils import db_add_class, db_show_class, db_show_teach_room
from app.db_utils.db_monitoring_utils import db_record_log

class_room_bp = Blueprint('class_room_bp', __name__, url_prefix = '/api/class_room')

@class_room_bp.post('/add_class')
@jwt_required()
@role_utils.required_role('admin')
def add_class_room():
    username = get_jwt_identity()
    class_room = request.get_json().get('class_room')
    year = request.get_json().get('year')
    errors = utils.class_validates(class_room, year)
    if errors:
        db_record_log(username, 'add class', 'FAIL', f'Add {class_room}:{errors}')
        return jsonify({'msg': errors}), 400
    db_add_class(class_room, year)
    db_record_log(username, 'add class', 'SUCCESS', f'Add: {class_room}')
    return jsonify({'msg': 'Thêm lớp thành công!'}), 200

@class_room_bp.put('/show_class_room')
@role_utils.required_role('admin', 'teacher')
@jwt_required()
def show_class():
    year = request.get_json().get('year')
    username = get_jwt_identity()
    role = get_jwt().get('role')
    data = db_show_class(year, username, role)
    return jsonify({'data': data}), 200

@class_room_bp.put('/show_teach_room')
@jwt_required()
@role_utils.required_role('teacher', 'admin')
def show_teach_room():
    year = request.get_json().get('year')
    username = get_jwt_identity()
    teach_room = db_show_teach_room(username, year)
    return jsonify({'data': teach_room}), 200


