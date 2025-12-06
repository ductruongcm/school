from flask import Blueprint
from app.utils import required_role, validate_input, ResponseBuilder
from flask_jwt_extended import jwt_required, get_jwt
from app.services import CloudService
from app.extensions import db
from app.repositories import CloudRepo
from app.schemas import CloudSchemas


cloud_bp = Blueprint('cloud_bp', __name__, url_prefix = '/api/cloud')
cloud_service = CloudService(db, CloudRepo)

@cloud_bp.post('/files')
@jwt_required()
@required_role('admin', 'Teacher')
@validate_input(CloudSchemas.Upload)
def upload(validated_data):
    validated_data['upload_by'] = get_jwt().get('id')
    result = cloud_service.handle_upload(validated_data)
    msg = f"Đã upload file {result['filename']} thành công!"
    return ResponseBuilder.post(msg, result['url'])

@cloud_bp.get('/files')
@jwt_required()
@required_role('admin', 'Teacher', 'Student')
@validate_input(CloudSchemas.ShowFileSchema)
def show_file(validated_data):
    result = cloud_service.handle_show_file(validated_data)
    return ResponseBuilder.get('Không có dữ liệu!', result)
 
@cloud_bp.get('/files/<int:id>')
@jwt_required()
def download(id: int):
    result = cloud_service.handle_download({'file_id': id})
    return ResponseBuilder.get('Không có dữ liệu!', result)

@cloud_bp.put('/files/<int:id>/hide')
@jwt_required()
@required_role('admin', 'Teacher')
def hide_files(id: int):
    file = cloud_service.handle_status({'file_id': id})
    msg = f"Đã ẩn file {file['filename']}!" if not file['status'] else f"Đã hiện file {file['filename']}!"
    return ResponseBuilder.put(msg)

@cloud_bp.delete('/files/<int:id>')
@jwt_required()
@required_role('admin', 'Teacher')
def delete(id: int):
    file = cloud_service.handle_delete({'file_id': id})
    msg = f"Đã xóa file {file['filename']}!"
    return ResponseBuilder.delete(msg)

@cloud_bp.get('/me/folders')
@jwt_required()
@required_role('admin', 'Teacher', 'Student')
@validate_input(CloudSchemas.ShowFolderSchema)
def show_folder(validated_data):
    validated_data.update({'user_id': get_jwt().get('id'),
                           'role': get_jwt().get('role')})
    result = cloud_service.handle_show_folders(validated_data)
    return ResponseBuilder.get('Không có dữ liệu!', result)


