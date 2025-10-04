from flask import Blueprint, jsonify
from app.utils import required_role, error_show_return
from flask_jwt_extended import jwt_required
from app.services import MonitoringService
from app.controllers import ClassroomsController, AcademicController

academic_bp = Blueprint('academic_bp', __name__, url_prefix = '/api/academic')

@academic_bp.post('/add_class')
@jwt_required()
@required_role('admin')
def add_class_room_route():
    result = ClassroomsController.add_class_room()
    if result['status'] == 'Validation_error':
        MonitoringService.handle_add_monitoring( result['username'], 'Add class room', 'FAIL', f"{result['class_room']}: {result['msg']}")
        return jsonify({'msg': result['msg']}), 422
       
    elif result['status'] == 'Logic_error':
        MonitoringService.handle_add_monitoring(result['username'], 'Add class room', 'FAIL', f"{result['class_room']}: {result['msg']}")
        return jsonify({'msg': result['msg']}), 400
    
    elif result['status'] == 'DB_error':
        MonitoringService.handle_add_monitoring(result['username'], 'Add class room', 'FAIL', f"{result['class_room']}: {result['msg']}")
        return jsonify({'msg': result['msg']}), 500
    
    else:
        return jsonify({'msg': result['msg']}), 200
    
@academic_bp.get('/class_rooms')
@required_role('admin', 'teacher')
@jwt_required()
def class_room_show():
    result = ClassroomsController.show_class_room()
    errors = error_show_return(result)
    if errors:
        return errors
    
    return jsonify({'data': result['data']}), 200

@academic_bp.get('/teach_rooms')
@jwt_required()
@required_role('teacher', 'admin')
def teach_room_show():
    result = ClassroomsController.show_teach_room()
    if result['status'] == 'DB_error':
  
        return jsonify({'msg': result['msg']}), 500
    
    return jsonify({'data': result['data']}), 200

@academic_bp.post('/years')
@jwt_required()
@required_role('admin')
def add_year_route():
    result = AcademicController.Add_controller.add_year()
    errors = error_show_return(result)
    if errors:
        return errors
    
    return jsonify({'msg': result['msg']}), 200

@academic_bp.post('/semesters')
@jwt_required()
@required_role('admin')
def add_semester_route():
    result = AcademicController.Add_controller.add_semester()
    errors = error_show_return(result)
    if errors:
        return errors
    
    return jsonify({'msg': result['msg']}), 200
    
@academic_bp.post('/lessons')
@required_role('admin')
@jwt_required()
def add_lesson_route():
    result = AcademicController.Add_controller.add_lesson()
    errors = error_show_return(result)
    if errors:
        return errors
    
    return jsonify({'msg': result['msg']}), 200
    
@academic_bp.post('/grades')
@jwt_required()
@required_role('admin')
def add_grade_route():
    result = AcademicController.Add_controller.add_grade()
    errors = error_show_return(result)
    if errors:
        return errors
    
    return jsonify({'msg': result['msg']}), 200

@academic_bp.get('/years')
@jwt_required()
@required_role('admin')
def show_year_route():
    result = AcademicController.Show_controller.show_year()
    errors = error_show_return(result)
    if errors:
        return errors
    
    return jsonify({'data': result['data']}), 200

@academic_bp.get('/semesters')
@jwt_required()
@required_role('admin')
def show_semester_route():
    result = AcademicController.Show_controller.show_semester()
    errors = error_show_return(result)
    if errors:
        return errors

    return jsonify({'data': result['data']}), 200

@academic_bp.get('/lessons')
@jwt_required()
@required_role('admin', 'teacher')
def show_lesson_route():
    result = AcademicController.Show_controller.show_lesson()
    errors = error_show_return(result)
    if errors:
        return errors

    return jsonify({'data': result['data']}), 200

@academic_bp.get('/grades')
@jwt_required()
@required_role('admin')
def show_grade_route():
    result = AcademicController.Show_controller.show_grade()
    errors = error_show_return(result)
    if errors:
        return errors

    return jsonify({'data': result['data']}), 200