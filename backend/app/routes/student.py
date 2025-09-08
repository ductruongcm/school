from flask import Blueprint, request, jsonify
from app.utils import utils, role_utils
from flask_jwt_extended import jwt_required
from app.db_utils.db_student_utils import db_add_student

student_bp = Blueprint('student_bp', __name__, url_prefix = '/api/student')

@student_bp.post('/add_student')
@jwt_required()
@role_utils.required_role('admin')
def add_student():
    errors = []
    name = request.get_json().get('name')
    errors.extend(utils.name_validates(name))
    class_room = request.get_json().get('class_room')
    year = request.get_json().get('year')
    errors.extend(utils.class_validates(class_room, year))
    tel = request.get_json().get('tel')
    errors.extend(utils.tel_validates(tel))
    add = request.get_json().get('add')
    errors.extend(utils.add_validates(add))
    role = request.get_json().get('role') or 'guest'
    if errors:
        print(errors)
        return jsonify({'msg': errors}), 400
    db_add_student(name, class_room, tel, add, role, year)
    return jsonify({'msg': 'Thêm học sinh mới thành công!'}), 200