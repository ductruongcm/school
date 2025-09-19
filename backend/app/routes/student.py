from flask import Blueprint, request, jsonify
from app.utils import utils, role_utils
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db_utils.db_student_utils import db_add_student, db_show_student, db_update_info
from app.db_utils.db_monitoring_utils import db_record_log

student_bp = Blueprint('student_bp', __name__, url_prefix = '/api/student')

@student_bp.post('/add_student')
@jwt_required()
@role_utils.required_role('admin', 'teacher')
def add_student():
    errors = []
    username = get_jwt_identity()
    name = request.get_json().get('name')
    class_room = request.get_json().get('class_room')
    year = request.get_json().get('year')
    tel = request.get_json().get('tel')
    add = request.get_json().get('add')
    role = request.get_json().get('role') or 'guest'
    errors = utils.errors(name = name, class_room = class_room, year = year, tel = tel, add = add)
    if errors:
        db_record_log(username, 'add student', 'FAIL', f'Add {name}: {errors}')
        return jsonify({'msg': errors}), 400
    db_record_log(username, 'add student', 'SUCCESS', f'Add: {name}')
    db_add_student(name, class_room, tel, add, role, year)
    return jsonify({'msg': 'Thêm học sinh mới thành công!'}), 200

@student_bp.get('/show_student')
@jwt_required()
@role_utils.required_role('admin', 'teacher')
def show_student():
    class_room = request.args.get('class_room')
    data = db_show_student(class_room)
    return jsonify({'data': data}), 200
    
@student_bp.put('/update_info')
@jwt_required()
@role_utils.required_role('admin')
def update_info():
    username = get_jwt_identity()
    student_id = request.get_json().get('id')
    name = request.get_json().get('name')
    tel = request.get_json().get('tel')
    add = request.get_json().get('add')
    errors = utils.errors(name = name, tel = tel, add = add)
    if errors:
        db_record_log(username, 'update student info', 'FAIL', f'Update {name}: {errors}')
        return jsonify({'msg': errors}), 400
    db_update_info(student_id, name, tel, add)
    db_record_log(username, 'update student info', 'SUCCESS', f'Update: {name}')
    return jsonify({'msg': 'Updated!'}), 200