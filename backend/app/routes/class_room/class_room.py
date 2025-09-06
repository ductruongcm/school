from flask import Blueprint, request, jsonify
from app.utils import role_utils
from flask_jwt_extended import get_jwt, jwt_required

class_room_bp = Blueprint('class_room_bp', __name__, url_prefix = '/api/class_room')


@class_room_bp.post('/add_class')
@jwt_required()
@role_utils.required_role('admin')
def add_class():
    data = request.get_json().get('class_room')
    
    print(data)
    return jsonify({'msg': 'ok'})
