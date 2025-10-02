from flask import Blueprint, request, jsonify
from app.utils import helpers, required_role
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.repositories.student import db_add_student, db_show_student, db_update_info, db_show_score
from app.services import Monitoring_service

student_bp = Blueprint('student_bp', __name__, url_prefix = '/api/student')

@student_bp.post('/add_student')
@jwt_required()
@required_role('admin', 'teacher')
def add_student():
    errors = []
    username = get_jwt_identity()
    name = request.get_json().get('name')
    class_room = request.get_json().get('class_room')
    year = request.get_json().get('year')
    tel = request.get_json().get('tel')
    add = request.get_json().get('add')
    role = request.get_json().get('role') or 'guest'

    errors = helpers.errors(name = name, class_room = class_room, year = year, tel = tel, add = add)
    if errors:
        Monitoring_service.handle_add_monitoring(username, 'add student', 'FAIL', f'Add {name}: {errors}')
        return jsonify({'msg': errors}), 400
   
    Monitoring_service.handle_add_monitoring(username, 'Add student', 'SUCCESS', f'Add: {name}')
    db_add_student(name, class_room, tel, add, role, year)
    return jsonify({'msg': 'Thêm học sinh mới thành công!'}), 200

@student_bp.get('/show_student')
@jwt_required()
@required_role('admin', 'teacher')
def show_student():
    class_room = request.args.get('class_room')
    data = db_show_student(class_room)
    return jsonify({'data': data}), 200
    
@student_bp.put('/update_info')
@jwt_required()
@required_role('admin')
def update_info():
    username = get_jwt_identity()
    student_id = request.get_json().get('id')
    name = request.get_json().get('name')
    tel = request.get_json().get('tel')
    add = request.get_json().get('add')
    errors = helpers.errors(name = name, tel = tel, add = add)
    if errors:
        Monitoring_service.handle_add_monitoring(username, 'update student info', 'FAIL', f'Update {name}: {errors}')
        return jsonify({'msg': errors}), 400
    
    db_update_info(student_id, name, tel, add)
    Monitoring_service.handle_add_monitoring(username, 'update student info', 'SUCCESS', f'Update: {name}')
    return jsonify({'msg': 'Updated!'}), 200

@student_bp.get('/show_score')
@jwt_required()
@required_role('admin', 'teacher')
def show_score():
    class_room = request.args.get('class_room')
    lesson = request.args.get('lesson')
    data = db_show_score(class_room, lesson)
    return jsonify({'data': data})