from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt
from app.extensions import lm, util, db
from app.utils import required_role, with_log, validate_input, ResponseBuilder
from app.schemas import SetPassword, Password, UserSchemas, Tmp_token, Register
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
    validated_data['user_id'] = get_jwt().get('id')
    user_workflow.process_change_password(validated_data)
    msg = 'Đã đặt lại mật khẩu!'
    return ResponseBuilder.put(msg)

@user_bp.get('/users/years/<int:id>/me')
@jwt_required()
def show_user_info_route(id):
    result = user_workflow.handle_show_user_info({'user_id': get_jwt().get('id'),
                                                  'role': get_jwt().get('role'),
                                                  'year_id': id})
    msg = 'Không tìm thấy dữ liệu!'
    return ResponseBuilder.get(msg, result)

@user_bp.post('/users/me/password')
@with_log(True)
@validate_input(SetPassword)
def set_password(validated_data):
    #Get tmp token, password and re-typing password
    #Query db, accept to set Password if True else deny
    result = user_workflow.process_set_password(validated_data)
    msg = f'Đã set password thành công!'
    return ResponseBuilder.post(msg)

@user_bp.post('/users/me/tmp-token')
@validate_input(Tmp_token)
@jwt_required()
def check_tmp_token_for_reset_password(validated_data):
    result = user_service.handle_check_tmp_token_for_set_password(validated_data)
    msg = 'Temp Token hợp lệ!'
    return ResponseBuilder.post(msg, result)

@user_bp.post('/register')
@lm.limit("5 per minute", key_func = util.get_remote_address)
@with_log(True)
@validate_input(Register)
def register(validated_data):
    user_workflow.process_register_account_for_admin(validated_data)
    msg = 'Đăng ký thành công!'
    return ResponseBuilder.post(msg)