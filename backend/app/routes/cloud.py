from flask import Blueprint, jsonify
from app.utils import required_role, error_show_return
from flask_jwt_extended import jwt_required
from app.services import MonitoringService, CloudService
from app.controllers import CloudController

cloud_bp = Blueprint('cloud_bp', __name__, url_prefix = '/api/cloud')

@cloud_bp.post('/files')
@jwt_required()
@required_role('admin', 'teacher')
def upload():
    result = CloudController.upload()
    errors = error_show_return(result)
    if errors:
        return errors
    
    return jsonify({'url': result['url']}), 201

@cloud_bp.get('/files')
@jwt_required()
@required_role('admin', 'teacher')
def show_file():
    data = CloudController.show_file()
    return jsonify(data), 200

@cloud_bp.get('/files/<int:id>/download')
@jwt_required()
def download(id: int):
    return CloudService.handle_download(id)

@cloud_bp.get('/folders')
@jwt_required()
@required_role('admin', 'teacher')
def show_folder():
    data = CloudController.show_folder()
    return jsonify({'data': data}), 200

@cloud_bp.put('/files/<int:id>/hide')
@jwt_required()
@required_role('admin', 'teacher')
def hide_files(id: int):
    result = CloudService.handle_hide(id)
    errors = error_show_return(result)
    if errors:
        return errors
    
    return jsonify({'msg': result['msg']}), 200

@cloud_bp.put('/files/<int:id>/unhide')
@jwt_required()
@required_role('admin', 'teacher')
def unhide_file(id: int):
    result = CloudService.handle_undhide(id)
    errors = error_show_return(result)
    if errors:
        return errors
    
    return jsonify({'msg': result['msg']}), 200

@cloud_bp.delete('/files/<int:id>')
@jwt_required()
@required_role('admin', 'teacher')
def delete(id: int):
    result = CloudController.delete_file(id)
    errors = error_show_return(result)
    if errors:
        return(errors)
    MonitoringService.handle_add_monitoring(result['username'], 'delete file', 'SUCCESS', f"Delete: {result['file_name']}")
    return {'msg': result['msg']}, 200



