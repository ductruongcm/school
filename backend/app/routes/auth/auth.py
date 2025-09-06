from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import get_jwt_identity, get_jwt, jwt_required, create_access_token, set_access_cookies, unset_jwt_cookies, create_refresh_token, set_refresh_cookies
from datetime import timedelta
from app.extensions import lm, util
from app.utils import utils
from werkzeug.security import generate_password_hash
from app.routes.auth import db_auth_utils


auth_bp = Blueprint('auth_bp', __name__, url_prefix = '/api/auth')

@auth_bp.post('/register')
@lm.limit("5 per minute", key_func = util.get_remote_address)
def register():
    data = request.get_json()
    username = data.get('username').strip()
    password = data.get('password').strip()
    repassword = data.get('repassword').strip()
    name = data.get('name').strip()
    email = data.get('email').strip()

    errors = utils.errors(username, password, repassword, name, email)
    
    if errors:
        return jsonify({'msg': errors}), 400
    hashed_password = generate_password_hash(password)
    db_auth_utils.register(username, hashed_password, name, email)

    return jsonify({'msg': "Đăng ký thành công"}),200

@auth_bp.post('/login')
@lm.limit("5 per minute", key_func = util.get_remote_address)
def login():
    data = request.get_json()
    username = data.get('username').strip()
    password = data.get('password').strip()

    error = utils.login_validates(username, password)
    if error:
        return jsonify({'msg': error}), 400
    
    role = db_auth_utils.role(username)
    access_token = create_access_token(identity = username, expires_delta = timedelta(minutes = 15), additional_claims = {'role': role})
    refresh_token = create_refresh_token(identity = username, expires_delta = timedelta(hours = 10), additional_claims = {'role': role})
    response = make_response('ok')
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response, 200


@auth_bp.get('/user_info')
@lm.limit("5 per minute", key_func = util.get_remote_address)
@jwt_required()
def user_info():
    username = get_jwt_identity()
    role = get_jwt().get('role') 
    name, email, tel, add, class_room = db_auth_utils.info(username)
    return jsonify({'username': username,
                    'role': role,
                    'name': name,
                    'email': email,
                    'tel': tel,
                    'add': add,
                    'class_room': class_room}), 200

@auth_bp.get('/refresh_token')
@jwt_required(refresh = True)
def refresh_token():
    # axios.get('url') là đã xác nhận đc refresh token
    # lấy thông tin, tạo mới access token
    # truyền thông tin qua res
    # đính kèm cookie chứa access token
    username = get_jwt_identity()
    role = get_jwt().get('role') 
    access_token = create_access_token(identity = username, 
                                       expires_delta = timedelta(minutes = 15),
                                       additional_claims = {'role': role})
    response = jsonify({'username': username, 'role': role})
    set_access_cookies(response, access_token)
    return response, 200

@auth_bp.get('/logout')
def logout():
    res = jsonify({'msg': 'logout successfully'})
    unset_jwt_cookies(res)
    return res
    