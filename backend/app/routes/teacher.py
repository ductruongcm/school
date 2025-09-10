from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required
from app.utils import role_utils, utils
from app.db_utils.db_teacher import db_add_lesson, db_add_teacher, db_show_teacher, db_show_lesson

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
    data = request.get_json()
    errors = []
    name = data.get('name').strip()
    errors.extend(utils.name_validates(name))
    lesson = data.get('lesson').strip()
    class_room = data.get('classRoom').strip()
    year = data.get('year').strip()
    errors.extend(utils.class_validates(class_room, year))
    tel = data.get('tel').strip()
    errors.extend(utils.tel_validates(tel))
    add = data.get('add').strip()
    errors.extend(utils.add_validates(add))
    email = data.get('email').strip()
    errors.extend(utils.email_validates(email))
    if errors:
        print(errors)
        return jsonify({'msg': errors}), 400
    db_add_teacher(name, lesson, class_room, tel, add, email)
    return jsonify({'msg': 'added!'}), 200

@teacher_bp.get('/show_lesson')
@role_utils.required_role('admin')
@jwt_required()
def show_lesson():
    data = db_show_lesson()
    return jsonify({'data': data}), 200
    
@teacher_bp.get('/show_teacher')
@role_utils.required_role('admin')
@jwt_required()
def show_teacher():
    lesson = request.args.get('lesson')
    class_room = request.args.get('class_room')
    name = request.args.get('name').title()
    data = db_show_teacher(lesson, class_room, name)
    return jsonify({'data': data}), 200