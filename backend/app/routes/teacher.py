from flask import jsonify, Blueprint
from flask_jwt_extended import jwt_required
from app.utils import required_role, error_show_return
from app.services import Monitoring_service
from app.controllers import Teacher_controller

teacher_bp = Blueprint('teacher_bp', __name__, url_prefix = '/api/teacher')

@teacher_bp.post('/add_teacher')
@required_role('admin')
@jwt_required()
def add_teacher():
    result = Teacher_controller.add_teacher()

    if result['status'] == 'Validation_error':
        Monitoring_service.handle_add_monitoring(result['username'], 'add teacher', 'FAIL', f'Add: {result['name']} - {result['msg']}')
        return jsonify({'msg': result['msg']}), 422
    
    elif result['status'] == 'Logic_error':
        Monitoring_service.handle_add_monitoring(result['username'], 'add teacher', 'FAIL', f'Add: {result['name']} - {result['msg']}')
        return jsonify({'msg': result['msg']}), 400
    
    elif result['status'] == 'DB_error':
        Monitoring_service.handle_add_monitoring(result['username'], 'add teacher', 'FAIL', f'Add: {result['name']} - {result['msg']}')
        return jsonify({'msg': result['msg']}), 500
    
    else:
        Monitoring_service.handle_add_monitoring(result['username'], 'add teacher', 'SUCCESS', f'Add: {result['name']}')
        return jsonify({'msg': result['msg']}), 200
  
@teacher_bp.get('/show_teacher')
@required_role('admin', 'teacher')
@jwt_required()
def show_teacher():
    result = Teacher_controller.show_teacher()
    errors = error_show_return(result)
    if errors:
        return errors

    return jsonify(result['data']), 200

@teacher_bp.put('/update_info')
@required_role('admin')
@jwt_required()
def update_info():
    result = Teacher_controller.update_teacher_info()
    print(result)
    if result['status'] == 'Validation_error':
        return jsonify({'msg': result['msg']}), 422
       
    elif result['status'] == 'Logic_error':
        return jsonify({'msg': result['msg']}), 400
    
    elif result['status'] == 'DB_error':
        return jsonify({'msg': result['msg']}), 500
    
    return jsonify({'msg': result['msg']}), 200
