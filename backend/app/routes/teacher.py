from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils import role_utils, utils
from app.db_utils.db_teacher_utils import db_add_lesson, db_add_teacher, db_show_teacher, db_show_lesson, db_update_info, db_update_teach_room
from app.db_utils.db_monitoring_utils import db_record_log

teacher_bp = Blueprint('teacher_bp', __name__, url_prefix = '/api/teacher')

@teacher_bp.post('/add_lesson')
@role_utils.required_role('admin')
@jwt_required()
def add_lesson():
    lesson = request.get_json().get('lesson')
    db_add_lesson(lesson)
    return jsonify({'msg': 'added!'})

@teacher_bp.post('/add_teacher')
@role_utils.required_role('admin')
@jwt_required()
def add_teacher():
    username = get_jwt_identity()
    data = request.get_json()
    name = data.get('name').strip()
    lesson = data.get('lesson').strip()
    class_room = data.get('class_room').strip()
    teach_room = data.get('teach_room').strip()
    year = data.get('year').strip()
    tel = data.get('tel').strip()
    add = data.get('add').strip()
    teacher_username = data.get('username').strip()
    email = data.get('email').strip()
    errors = utils.errors(name = name, tel = tel, username = teacher_username, email = email, add = add, class_room = teach_room, year = year)
    if errors:
        db_record_log(username, 'add teacher', 'FAIL', f'Add {name}: {errors}')
        return jsonify({'msg': errors}), 400
    db_add_teacher(name = name, 
                   current_lesson = lesson, 
                   current_class_room = class_room, 
                   current_teach_room = teach_room, 
                   tel = tel, add = add, email = email, 
                   username = teacher_username)
    db_record_log(username, 'add teacher', 'SUCCESS', f'Add: {name}')
    return jsonify({'msg': 'added!'}), 200

@teacher_bp.get('/show_lesson')
@role_utils.required_role('admin', 'teacher')
@jwt_required()
def show_lesson():
    username = get_jwt_identity()
    data = db_show_lesson(username)
    return jsonify({'data': data}), 200
    
@teacher_bp.get('/show_teacher')
@role_utils.required_role('admin', 'teacher')
@jwt_required()
def show_teacher():
    lesson = request.args.get('lesson')
    class_room = request.args.get('class_room')
    name = request.args.get('name').title()
    data = db_show_teacher(lesson, class_room, name)
    if not data:
        return jsonify({'msg': 'Không tìm thấy thông tin!'}), 400
    return jsonify({'data': data}), 200

@teacher_bp.put('/update_info')
@role_utils.required_role('admin')
@jwt_required()
def update_info():
    username = get_jwt_identity()
    teacher_id = request.get_json().get('id')
    name = request.get_json().get('name')
    lesson = request.get_json().get('lesson')
    class_room = request.get_json().get('class_room')
    teach_room = request.get_json().get('teach_room')
    tel = request.get_json().get('tel')
    add = request.get_json().get('add')
    email = request.get_json().get('email')
    year = request.get_json().get('year')
    errors = utils.errors(name = name, tel = tel, add = add, role = 'teacher', email = email, year = year, class_room = class_room)

    if errors:
        db_record_log(username, 'update teacher info', 'FAIL', f'Update {name}: {errors}')
        return jsonify({'msg': errors}), 400
    db_update_info(teacher_id, name, lesson, class_room, tel, add, email)
    db_update_teach_room(teacher_id, teach_room)
    db_record_log(username, 'update teacher info', 'SUCCESS', f'Update: {name}')
    return jsonify({'msg': 'Updated!!'}), 200

