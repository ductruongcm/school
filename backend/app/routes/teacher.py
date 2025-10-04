from flask import jsonify, Blueprint
from flask_jwt_extended import jwt_required
from app.utils import required_role, error_show_return
from app.services import MonitoringService
from app.controllers import TeacherController

teacher_bp = Blueprint('teacher_bp', __name__, url_prefix = '/api/teacher')

@teacher_bp.post('/teachers')
@required_role('admin')
@jwt_required()
def add_teacher():
    result = TeacherController.add_teacher()

    if result['status'] == 'Validation_error':
        MonitoringService.handle_add_monitoring(result['username'], 'add teacher', 'FAIL', f'Add: {result['name']} - {result['msg']}')
        return jsonify({'msg': result['msg']}), 422
    
    elif result['status'] == 'Logic_error':
        MonitoringService.handle_add_monitoring(result['username'], 'add teacher', 'FAIL', f'Add: {result['name']} - {result['msg']}')
        return jsonify({'msg': result['msg']}), 400
    
    elif result['status'] == 'DB_error':
        MonitoringService.handle_add_monitoring(result['username'], 'add teacher', 'FAIL', f'Add: {result['name']} - {result['msg']}')
        return jsonify({'msg': result['msg']}), 500
    
    else:
        MonitoringService.handle_add_monitoring(result['username'], 'add teacher', 'SUCCESS', f'Add: {result['name']}')
        return jsonify({'msg': result['msg']}), 200
  
@teacher_bp.get('/teachers')
@required_role('admin', 'teacher')
@jwt_required()
def show_teacher():
    result = TeacherController.show_teacher()
    errors = error_show_return(result)
    if errors:
        return errors

    return jsonify(result['data']), 200

@teacher_bp.put('/teacher_info')
@required_role('admin')
@jwt_required()
def update_info():
    result = TeacherController.update_teacher_info()
    print(result)
    if result['status'] == 'Validation_error':
        return jsonify({'msg': result['msg']}), 422
       
    elif result['status'] == 'Logic_error':
        return jsonify({'msg': result['msg']}), 400
    
    elif result['status'] == 'DB_error':
        return jsonify({'msg': result['msg']}), 500
    
    return jsonify({'msg': result['msg']}), 200
