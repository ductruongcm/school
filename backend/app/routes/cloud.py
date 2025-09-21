from flask import Blueprint, request, jsonify
from app.utils.cloud_utils import cloud_upload, cloud_download, cloud_delete
from app.utils.role_utils import required_role
from app.db_utils.db_cloud_ultis import db_upload, db_show_folder, db_hide_file, db_unhide_file, db_delete, db_show_file
from app.utils.utils import filename_validates
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db_utils.db_monitoring_utils import db_record_log

cloud_bp = Blueprint('cloud_bp', __name__, url_prefix = '/api/cloud')

@cloud_bp.post('/upload')
@jwt_required()
@required_role('admin', 'teacher')
def upload():
    file_ext = request.form.get('fileExtension').split('.')[1]
    file_name = request.form.get('fileName')+f'.{file_ext}'
    file_size = request.form.get('fileSize')
    file_type = request.form.get('fileType')
    class_room = request.form.get('classRoom')
    folder = request.form.get('folder')
    username = get_jwt_identity()
    
    errors = filename_validates(class_room, file_name)
    if errors:
        db_record_log(username, 'upload', 'FAIL', f'Upload {file_name}: {errors}')
        return jsonify({'msg': errors}), 400
    url = cloud_upload(class_room, folder, file_name)
    db_upload(username, file_name, file_size, file_type, class_room, folder)
    db_record_log(username, 'upload', 'SUCCESS', f'Upload: {file_name}')
    return jsonify({'url': url}), 200

@cloud_bp.get('/show_folder')
@jwt_required()
def show_folder():
    class_room = request.args.get('class_room')
    data = db_show_folder(class_room)
    return jsonify({'data': data}), 200

@cloud_bp.get('/show_file')
@jwt_required()
def show_file():
    class_room = request.args.get('class_room')
    folder = request.args.get('folder')
    data = db_show_file(class_room, folder)
    return jsonify({'data': data}), 200

@cloud_bp.put('/hide_file')
@jwt_required()
@required_role('admin', 'teacher')
def hide_file():
    file_name = request.get_json().get('file_name')
    class_room = request.args.get('class_room')

    db_hide_file(class_room, file_name)
    return jsonify({'msg': 'ok'}), 200

@cloud_bp.put('/unhide_file')
@jwt_required()
@required_role('admin', 'teacher')
def unhide_file():
    file_name = request.get_json().get('file_name')
    class_room = request.args.get('class_room')
    db_unhide_file(class_room, file_name)
    return jsonify({'msg': 'ok'}), 200

@cloud_bp.put('/download')
@jwt_required()
def download():
    file_name = request.get_json().get('file_name')
    class_room = request.get_json().get('class_room')
    url = cloud_download(class_room, file_name)
    return jsonify({'url': url}), 200

@cloud_bp.delete('/delete')
@jwt_required()
@required_role('admin', 'teacher')
def delete():
    username = get_jwt_identity()
    file_name = request.args.get('file_name')
    class_room = request.args.get('class_room')

    url = cloud_delete(class_room, file_name)
    db_delete(class_room, file_name)
    db_record_log(username, 'delete file', 'SUCCESS', f'Delete: {file_name}')
    return jsonify({'url': url}), 200



