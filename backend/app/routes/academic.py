from flask import Blueprint, jsonify
from app.utils import required_role, error_show_return
from flask_jwt_extended import jwt_required
from app.services import Monitoring_service
from app.controllers import Class_room_controller, Academic_controller

academic_bp = Blueprint('academic_bp', __name__, url_prefix = '/api/academic')

@academic_bp.post('/add_class')
@jwt_required()
@required_role('admin')
def add_class_room_route():
    result = Class_room_controller.add_class_room()
    if result['status'] == 'Validation_error':
        Monitoring_service.handle_add_monitoring( result['username'], 'Add class room', 'FAIL', f"{result['class_room']}: {result['msg']}")
        return jsonify({'msg': result['msg']}), 422
       
    elif result['status'] == 'Logic_error':
        Monitoring_service.handle_add_monitoring(result['username'], 'Add class room', 'FAIL', f"{result['class_room']}: {result['msg']}")
        return jsonify({'msg': result['msg']}), 400
    
    elif result['status'] == 'DB_error':
        Monitoring_service.handle_add_monitoring(result['username'], 'Add class room', 'FAIL', f"{result['class_room']}: {result['msg']}")
        return jsonify({'msg': result['msg']}), 500
    
    else:
        return jsonify({'msg': result['msg']}), 200
    
@academic_bp.get('/show_class_room')
@required_role('admin', 'teacher')
@jwt_required()
def show_class_route():
    result = Class_room_controller.show_class_room()
    errors = error_show_return(result)
    if errors:
        return errors
    
    return jsonify({'data': result['data']}), 200

@academic_bp.put('/show_teach_room')
@jwt_required()
@required_role('teacher', 'admin')
def show_teach_room_route():
    result = Class_room_controller.show_teach_room()
    if result['status'] == 'DB_error':
        return jsonify({'msg': result['msg']}), 500
    
    return jsonify({'data': result['data']}), 200

@academic_bp.post('/add_year')
@jwt_required()
@required_role('admin')
def add_year_route():
    result = Academic_controller.Add_controller.add_year()
    errors = error_show_return(result)
    if errors:
        return errors
    
    return jsonify({'msg': result['msg']}), 200

@academic_bp.post('/add_semester')
@jwt_required()
@required_role('admin')
def add_semester_route():
    result = Academic_controller.Add_controller.add_semester()
    errors = error_show_return(result)
    if errors:
        return errors
    
    return jsonify({'msg': result['msg']}), 200
    
@academic_bp.post('/add_lesson')
@required_role('admin')
@jwt_required()
def add_lesson_route():
    result = Academic_controller.Add_controller.add_lesson()
    errors = error_show_return(result)
    if errors:
        return errors
    
    return jsonify({'msg': result['msg']}), 200
    
@academic_bp.post('/add_grade')
@jwt_required()
@required_role('admin')
def add_grade_route():
    result = Academic_controller.Add_controller.add_grade()
    errors = error_show_return(result)
    if errors:
        return errors
    
    return jsonify({'msg': result['msg']}), 200

@academic_bp.get('/show_year')
@jwt_required()
@required_role('admin')
def show_year_route():
    result = Academic_controller.Show_controller.show_year()
    errors = error_show_return(result)
    if errors:
        return errors
    
    return jsonify({'data': result['data']}), 200

@academic_bp.get('/show_semester')
@jwt_required()
@required_role('admin')
def show_semester_route():
    result = Academic_controller.Show_controller.show_semester()
    errors = error_show_return(result)
    if errors:
        return errors

    return jsonify({'data': result['data']}), 200

@academic_bp.get('/show_lesson')
@jwt_required()
@required_role('admin', 'teacher')
def show_lesson_route():
    result = Academic_controller.Show_controller.show_lesson()
    errors = error_show_return(result)
    if errors:
        return errors

    return jsonify({'data': result['data']}), 200

@academic_bp.get('/show_grade')
@jwt_required()
@required_role('admin')
def show_grade_route():
    result = Academic_controller.Show_controller.show_grade()
    errors = error_show_return(result)
    if errors:
        return errors

    return jsonify({'data': result['data']}), 200