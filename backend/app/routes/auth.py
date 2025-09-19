from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import get_jwt_identity, jwt_required, create_access_token, set_access_cookies, unset_jwt_cookies, create_refresh_token, set_refresh_cookies
from datetime import timedelta, datetime
from app.extensions import lm, util
from app.utils import utils
from werkzeug.security import generate_password_hash
from app.db_utils import db_auth_utils
from app.db_utils.db_monitoring_utils import db_record_log



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

@auth_bp.put('/login')
@lm.limit("5 per minute", key_func = util.get_remote_address)
def login():
    data = request.get_json()
    username = data.get('username').strip()
    password = data.get('password').strip()
    errors = utils.login_validates(username, password)
    if errors:
        db_record_log(username, 'login', 'FAIL', f'Login: {errors}')
        return jsonify({'msg': errors}), 400
    
    role, id = db_auth_utils.role(username)
    access_token = create_access_token(identity = username, expires_delta = timedelta(minutes = 15), additional_claims = {'role': role, 'id': id})
    refresh_token = create_refresh_token(identity = username, expires_delta = timedelta(hours = 10), additional_claims = {'role': role, 'id': id})
    response = make_response(jsonify({'id': id,
                    'username': username,
                    'role': role,
                    'editing': False,
                    'expired_at': datetime.utcnow() + timedelta(minutes=15)}))
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response, 200

@auth_bp.get('/refresh_token')
@jwt_required(refresh = True)
def refresh_token():
    # axios.get('url') là đã xác nhận đc refresh token
    # lấy thông tin, tạo mới access token
    # truyền thông tin qua res
    # đính kèm cookie chứa access token
    username = get_jwt_identity()
    role, id = db_auth_utils.role(username)
    access_token = create_access_token(identity = username, 
                                       expires_delta = timedelta(minutes = 15),
                                       additional_claims = {'role': role, 'id': id})

    response = make_response(jsonify({'id': id,
                    'username': username,
                    'role': role,
                    'editing': False,
                    'expired_at': datetime.utcnow() + timedelta(minutes=15)}))
    set_access_cookies(response, access_token)
    return response, 200

@auth_bp.get('/logout')
def logout():
    res = jsonify({'msg': 'logout successfully'})
    unset_jwt_cookies(res)
    return res
    