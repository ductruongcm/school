from flask import Blueprint, jsonify, make_response
from flask_jwt_extended import jwt_required, set_access_cookies, set_refresh_cookies, unset_jwt_cookies
from app.controllers import UsersController, AuthController
from app.extensions import lm, util
from app.services import MonitoringService
from app.utils import required_role, error_show_return
from datetime import timedelta, datetime
from app.services import AuthService

user_bp = Blueprint('user_bp', __name__, url_prefix = '/api/user')

@user_bp.post('/register')
@lm.limit("5 per minute", key_func = util.get_remote_address)
def register():
    result = AuthController.register()
    if result['status'] == 'Validation_error':
        MonitoringService.handle_add_monitoring(result['username'], 'Register', 'FAIL', f"{result['username']}: {result['msg']}")
        return jsonify({'msg': result['msg']}), 422
    
    elif result['status'] == 'Logic_error':
        MonitoringService.handle_add_monitoring(result['username'], 'Register', 'FAIL', f"{result['username']}: {result['msg']}")
        return jsonify({'msg': result['msg']}), 400
    
    elif result['status'] == 'DB_error':
        MonitoringService.handle_add_monitoring(result['username'], 'Register', 'FAIL', f"{result['username']}: {result['msg']}")
        return jsonify({'msg': result['msg']}), 500
    
    else:
        MonitoringService.handle_add_monitoring(result['username'], 'Register', 'SUCCESS', f"{result['username']}: {result['msg']}")
        return jsonify({'msg': result['msg']}), 200

@user_bp.post('/login')
@lm.limit("5 per minute", key_func = util.get_remote_address)
def login():
    result = AuthController.login()
    if result['status'] == 'Validation_error':
        MonitoringService.handle_add_monitoring(result['username'], 'login', 'FAIL', f"Login: {result['msg']}")
        return jsonify({result['msg']}), 422

    if result['status'] == 'Logic_error':
        MonitoringService.handle_add_monitoring(result['username'], 'login', 'FAIL', f"Login: {result['msg']}")
        return jsonify({result['msg']}), 400
     
    response = make_response(jsonify({
                    'id':result['id'],
                    'username': result['username'],
                    'role': result['role'],
                    'editing': False,
                    'expired_at': datetime.utcnow() + timedelta(minutes=15)}))
    
    set_access_cookies(response, result['access_token'])
    set_refresh_cookies(response, result['refresh_token'])
    return response, 200

@user_bp.post('/refresh_token')
@jwt_required(refresh = True)
def refresh_token():
    # axios.get('url') là đã xác nhận đc refresh token
    # lấy thông tin, tạo mới access token
    # truyền thông tin qua res
    # đính kèm cookie chứa access token  
    result = AuthController.refresh_token()
    if result['status']:
        response = make_response(jsonify({
                    'id': result['id'],
                    'username': result['username'],
                    'role': result['role'],
                    'editing': False,
                    'expired_at': datetime.utcnow() + timedelta(minutes=15)}))
        set_access_cookies(response, result['access_token'])
        return response, 200

@user_bp.get('/logout')
def logout():
    res = jsonify({'msg': 'logout successfully'})
    unset_jwt_cookies(res)
    return res

@user_bp.get('/users')
@jwt_required()
@required_role('admin')
def show_users():
    result = UsersController.show_user()

    errors = error_show_return(result)
    if errors:
        return errors
 
    return jsonify(result['data']), 200

@user_bp.put('/user_info')
@lm.limit("5 per minute", key_func = util.get_remote_address)
@jwt_required()
def update_info():
    result = UsersController.update_info()
    if result['status'] == 'Validation_error':
        MonitoringService.handle_add_monitoring(result['username'], 'Update user info', 'FAIL', f"{result['username']}: {result['msg']}")
        return {'msg': result['msg']}, 422
    
    elif result['status'] == 'Logic_error':
        MonitoringService.handle_add_monitoring(result['username'], 'Update user info', 'FAIL', f"{result['username']}: {result['msg']}")
        return {'msg': result['msg']}, 400

    elif result['status'] == 'DB_error':
        MonitoringService.handle_add_monitoring(result['username'], 'Update user info', 'FAIL', f"{result['username']}: {result['msg']}")
        return jsonify({'msg': result['msg']}), 500
    
    else:
        MonitoringService.handle_add_monitoring(result['username'], 'Update user info', 'SUCCESS', f'Update info: {result['username']}')
        return jsonify({'msg': 'Cập nhật thành công!!'}), 200

@user_bp.put('/password')
@jwt_required()
@lm.limit("5 per minute", key_func = util.get_remote_address)
def reset_password():
    result = UsersController.reset_password()
    errors = error_show_return(result)
    if errors:
        return errors
        # MonitoringService.handle_add_monitoring(username, 'Reset password', 'FAIL', f'Reset password: {errors}')
       
    # MonitoringService.handle_add_monitoring(username, 'Reset password', 'SUCCESS', f'Reset password: {username}')
    return jsonify({'msg': 'Đổi mật khẩu thành công'}), 200

# @user_bp.put('/update_role')
# @jwt_required()
# @required_role('admin')
# def update_role():
#     username = request.get_json().get('username')
#     role = request.get_json().get('role')
#     user.db_update_role(username, role)
#     return jsonify({'msg': f'Đã đổi role thành {role}'}), 200

@user_bp.get('/user_info')
@jwt_required()
def show_user_info_route():
    data = UsersController.show_user_info()
    return jsonify(data), 200

@user_bp.post('/tmp_token')
def check_tmp_token():
    #Get tmp token to check if ok and still valid or not
    result = AuthController.check_tmp_token()
    if result['status'] == 'DB_error':
        return jsonify({'msg': result['msg']}), 500
    
    else:
        return jsonify({'msg': 'Token hợp lệ'}), 200
    
@user_bp.put('/tmp_token/<int:user_id>')
@jwt_required()
@required_role('admin')
def reset_tmp_token(user_id):
    result = AuthService.renew_tmp_token(user_id)
    errors = error_show_return(result)
    if errors:
        return errors
    
    return jsonify({'msg': 'Cấp lại Tmp Token thành công!'})

@user_bp.post('/password')
def set_password():
    #Get tmp token, password and re-typing password
    #Query db, accept to set Password if True else deny
    
    result = AuthController.set_password()

    if result['status'] == 'Validation_error':
        MonitoringService.handle_add_monitoring(result['user_id'], 'Set password', 'FAIL', f"{result['user_id']}: {result['msg']}")
        return {'msg': result['msg']}, 422
    
    elif result['status'] == 'Logic_error':
        MonitoringService.handle_add_monitoring(result['user_id'], 'Set password', 'FAIL', f"{result['user_id']}: {result['msg']}")
        return {'msg': result['msg']}, 400

    elif result['status'] == 'DB_error':
        MonitoringService.handle_add_monitoring(result['user_id'], 'Set password', 'FAIL', f"{result['user_id']}: {result['msg']}")
        return jsonify({'msg': result['msg']}), 500
    
    else:
        MonitoringService.handle_add_monitoring(result['user_id'], 'Set password', 'SUCCESS', f"{result['user_id']}: {result['msg']}")
        return jsonify({'msg': result['msg']}), 200