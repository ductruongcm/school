from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, set_access_cookies, set_refresh_cookies, unset_jwt_cookies
from app.controllers import User_controller
from app.extensions import lm, util
from app.repositories import user
from werkzeug.security import generate_password_hash
from app.services import Auth_service, Monitoring_service, User_service
from app.utils import helpers, required_role
from datetime import timedelta, datetime

user_bp = Blueprint('user_bp', __name__, url_prefix = '/api/user')

@user_bp.post('/register')
@lm.limit("5 per minute", key_func = util.get_remote_address)
def register():
    data = request.get_json()

    result = Auth_service.handle_register(data)
    if result['status'] == 'Validation_error':
        Monitoring_service.handle_add_monitoring(data.get('username'), 'Register', 'FAIL', f"{data.get('username')}: {result['msg']}")
        return jsonify({'msg': result['msg']}), 422
    
    elif result['status'] == 'Logic_error':
        Monitoring_service.handle_add_monitoring(data.get('username'), 'Register', 'FAIL', f"{data.get('username')}: {result['msg']}")
        return jsonify({'msg': result['msg']}), 400
    
    elif result['status'] == 'DB_error':
        Monitoring_service.handle_add_monitoring(data.get('username'), 'Register', 'FAIL', f"{data.get('username')}: {result['msg']}")
        return jsonify({'msg': result['msg']}), 500
    
    else:
        Monitoring_service.handle_add_monitoring(data.get('username'), 'Register', 'SUCCESS', f"{data.get('username')}: {result['msg']}")
        return jsonify({'msg': result['msg']}), 200

@user_bp.post('/login')
@lm.limit("5 per minute", key_func = util.get_remote_address)
def login():
    data = request.get_json()

    auth = Auth_service.handle_login(data)
    if auth['status'] == 'Validation_error':
        Monitoring_service.handle_add_monitoring(data.get('username'), 'login', 'FAIL', f"Login: {auth['msg']}")
        return jsonify({'msg': auth['msg']}), 422

    if auth['status'] == 'Logic_error':
        Monitoring_service.handle_add_monitoring(data.get('username'), 'login', 'FAIL', f"Login: {auth['msg']}")
        return jsonify({'msg': auth['msg']}), 400
     
    response = make_response(jsonify({
                    'id': auth['id'],
                    'username': data.get('username'),
                    'role': auth['role'],
                    'editing': False,
                    'expired_at': datetime.utcnow() + timedelta(minutes=15)}))
    
    set_access_cookies(response, auth['access_token'])
    set_refresh_cookies(response, auth['refresh_token'])
    return response, 200

@user_bp.post('/refresh_token')
@jwt_required(refresh = True)
def refresh_token():
    # axios.get('url') là đã xác nhận đc refresh token
    # lấy thông tin, tạo mới access token
    # truyền thông tin qua res
    # đính kèm cookie chứa access token
    username = get_jwt_identity()

    result = Auth_service.handle_refresh_token(username)
    if result['status']:
        response = make_response(jsonify({
                    'id': result['id'],
                    'username': username,
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

@user_bp.get('show_users')
@jwt_required()
@required_role('admin')
def show_users():
    data = request.args.to_dict()

    result = User_service.handle_show_user(data)
    if result['status'] == 'Validation_error':
        return {'msg': result['msg']}
    
    elif result['status'] == 'Logic_error':
        return {'msg': result['msg']}
    
    else:
        return jsonify(result['data']), 200

@user_bp.put('/update_info')
@lm.limit("5 per minute", key_func = util.get_remote_address)
@jwt_required()
def update_info():
    username = get_jwt_identity()
    data = request.get_json() or {}

    result = User_service.handle_update_user_info(data)
    if result['status'] == 'Validation_error':
        Monitoring_service.handle_add_monitoring(username, 'Update user info', 'FAIL', f"{username}: {result['msg']}")
        return {'msg': result['msg']}, 422
    
    elif result['status'] == 'Logic_error':
        Monitoring_service.handle_add_monitoring(username, 'Update user info', 'FAIL', f"{username}: {result['msg']}")
        return {'msg': result['msg']}, 400

    elif result['status'] == 'DB_error':
        Monitoring_service.handle_add_monitoring(username, 'Update user info', 'FAIL', f"{username}: {result['msg']}")
        return jsonify({'msg': result['msg']}), 500
    
    else:
        Monitoring_service.handle_add_monitoring(username, 'Update user info', 'SUCCESS', f'Update info: {username}')
        return jsonify({'msg': 'Cập nhật thành công!!'}), 200

@user_bp.put('/reset_password')
@jwt_required()
@lm.limit("5 per minute", key_func = util.get_remote_address)
def reset_password():
    username = get_jwt_identity()
    password = request.get_json()['password'].strip()
    re_password = request.get_json()['re_password'].strip()

    errors = helpers.password_validates(password, re_password)
    if errors:
        Monitoring_service.handle_add_monitoring(username, 'Reset password', 'FAIL', f'Reset password: {errors}')
        return jsonify({'msg': errors}), 400
    
    hashed_password = generate_password_hash(password)
    user.db_reset_password(username, hashed_password)
    Monitoring_service.handle_add_monitoring(username, 'Reset password', 'SUCCESS', f'Reset password: {username}')
    return jsonify({'msg': 'Đổi mật khẩu thành công'}), 200

@user_bp.put('/update_role')
@jwt_required()
@required_role('admin')
def update_role():
    username = request.get_json().get('username')
    role = request.get_json().get('role')
    user.db_update_role(username, role)
    return jsonify({'msg': f'Đã đổi role thành {role}'}), 200

@user_bp.get('/show_user_info')
@jwt_required()
def show_user_info_route():
    data = User_controller.show_user_info()
    print(data)
    return jsonify(data), 200

@user_bp.post('/check_tmp_token')
def check_tmp_token():
    #Get tmp token to check if ok and still valid or not
    data = request.get_json().get('token')

    result = Auth_service.handle_check_tmp_token(data)
    if result['status'] == 'DB_error':
        return jsonify({'msg': result['msg']}), 500
    
    else:
        return jsonify({'msg': 'Token hợp lệ'}), 200

@user_bp.post('/set_password')
def set_password():
    #Get tmp token, password and re-typing password
    #Query db, accept to set Password if True else deny
    data = request.get_json()
    result = User_service.handle_set_password(data)

    if result['status'] == 'Validation_error':
        Monitoring_service.handle_add_monitoring(data['user_id'], 'Set password', 'FAIL', f"{data['user_id']}: {result['msg']}")
        return {'msg': result['msg']}, 422
    
    elif result['status'] == 'Logic_error':
        Monitoring_service.handle_add_monitoring(data['user_id'], 'Set password', 'FAIL', f"{data['user_id']}: {result['msg']}")
        return {'msg': result['msg']}, 400

    elif result['status'] == 'DB_error':
        Monitoring_service.handle_add_monitoring(data['user_id'], 'Set password', 'FAIL', f"{data['user_id']}: {result['msg']}")
        return jsonify({'msg': result['msg']}), 500
    
    else:
        Monitoring_service.handle_add_monitoring(data['user_id'], 'Set password', 'SUCCESS', f"{data['user_id']}: {result['msg']}")
        return jsonify({'msg': result['msg']}), 200