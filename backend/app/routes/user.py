from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt
from app.extensions import lm, util, db
from app.utils import required_role, with_log, validate_input, ResponseBuilder
from app.schemas import SetPassword, Password, UserSchemas
from app.services import UserService, User_Workflow
from app.repositories import Repositories

user_bp = Blueprint('user_bp', __name__, url_prefix = '/api')
user_service = UserService(db, Repositories)
user_workflow = User_Workflow(db, Repositories)

@user_bp.get('/users')
@jwt_required()
@required_role('admin')
@with_log(True)
@validate_input(UserSchemas.UserShowSchema)
def show_users(validated_data):
    result = user_service.handle_show_user(validated_data)
    msg = 'Thông tin tìm kiếm không có dữ liệu!'
    return ResponseBuilder.get(msg, result)

@user_bp.put('/users/me')
@lm.limit("5 per minute", key_func = util.get_remote_address)
@jwt_required()
@with_log(True)
@validate_input(UserSchemas.UserInfoUpdateSchema)
def update_info(validated_data):
    validated_data.update({'user_id': get_jwt().get('id'),
                           'role': get_jwt().get('role')})
    
    user_workflow.handle_update_user_info(validated_data)
    msg = f'Đã cập nhật thông tin!' 
        
    return ResponseBuilder.put(msg)
    
@user_bp.put('/users/me/password')
@jwt_required()
@with_log(True)
@validate_input(Password)
@lm.limit("5 per minute", key_func = util.get_remote_address)
def reset_password(validated_data):
    if validated_data == {}:
        msg = 'Không có thay đổi gì!'

    else:
        validated_data['user_id'] = get_jwt().get('id')
        result = user_service.handle_reset_password(validated_data)
        msg = f'Tài khoản {result.username} đã đặt lại mật khẩu!'
    return ResponseBuilder.put(msg)

@user_bp.get('/users/me')
@jwt_required()
def show_user_info_route():
    result = user_workflow.handle_show_user_info({'user_id': get_jwt().get('id'),
                                                'role': get_jwt().get('role')})
    msg = 'Không tìm thấy dữ liệu!'
    return ResponseBuilder.get(msg, result)

@user_bp.put('/users/<int:id>/tmp_token')
def reset_tmp_token(id):
    result = user_service.handle_renew_tmp_token({'user_id': id,
                                                  'role': 'Teacher'})
    msg = f'Đã cấp lại tmp_token cho user {result.username}'
    return ResponseBuilder.put(msg)

@user_bp.post('/users/<int:id>/password')
@with_log(True)
@validate_input(SetPassword)
def set_password(id: int, validated_data):
    #Get tmp token, password and re-typing password
    #Query db, accept to set Password if True else deny
    validated_data['user_id'] = id
    result = user_service.handle_set_password(validated_data)
    msg = f'{result.username} đã set password thành công!'
    return ResponseBuilder.post(msg)
