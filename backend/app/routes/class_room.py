from flask import Blueprint, request, jsonify
from app.utils import role_utils, utils
from flask_jwt_extended import jwt_required
from app.db_utils.db_class_room_utils import db_add_class, db_show_class

class_room_bp = Blueprint('class_room_bp', __name__, url_prefix = '/api/class_room')

@class_room_bp.post('/add_class')
@jwt_required()
@role_utils.required_role('admin')
def add_class_room():
    class_room = request.get_json().get('class_room')
    year = request.get_json().get('year')
    errors = utils.class_validates(class_room, year)
    if errors:
        return jsonify({'msg': errors}), 400
    db_add_class(class_room, year)
    return jsonify({'msg': 'Thêm lớp thành công!'}), 200

@class_room_bp.put('/show_class_room')
@jwt_required()
def show_class():
    year = request.get_json().get('year')
    data = db_show_class(year)
    return jsonify({'msg': 'ok', 'data': data})

    
