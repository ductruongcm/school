from flask import Blueprint, jsonify, make_response
from app.utils import with_log, validate_input
from app.extensions import lm, util, db
from datetime import datetime, timedelta
from app.schemas import Login, Register
from app.services import AuthService
from app.repositories import UsersRepo
from flask_jwt_extended import jwt_required, set_access_cookies, set_refresh_cookies, unset_jwt_cookies, get_jwt_identity

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/auth')
auth_service = AuthService(db, UsersRepo)

@auth_bp.post('/register')
@lm.limit("5 per minute", key_func = util.get_remote_address)
@with_log(True)
@validate_input(Register)
def register(validated_data):
    result = auth_service.handle_register(validated_data)
    return jsonify({'msg': result['msg']}), 200

@auth_bp.post('/login')
@lm.limit("5 per minute", key_func = util.get_remote_address)
@with_log(True)
@validate_input(Login)
def login(validated_data):
    result = auth_service.handle_login(validated_data)
    response = make_response(jsonify({
                    'id':result['id'],
                    'username': result['username'],
                    'role': result['role'],
                    'editing': False,
                    'expired_at': datetime.utcnow() + timedelta(minutes=15)}))
    
    set_access_cookies(response, result['access_token'])
    set_refresh_cookies(response, result['refresh_token'])
    return response, 200

@auth_bp.post('/refresh_token')
@jwt_required(refresh = True)
def refresh_token():
    # axios.get('url') là đã xác nhận đc refresh token
    # lấy thông tin, tạo mới access token
    # truyền thông tin qua res
    # đính kèm cookie chứa access token  
    result = auth_service.handle_refresh_token({'username': get_jwt_identity()})
    if result['status']:
        response = make_response(jsonify({
                    'id': result['id'],
                    'username': result['username'],
                    'role': result['role'],
                    'editing': False,
                    'expired_at': datetime.utcnow() + timedelta(minutes=15)}))
        set_access_cookies(response, result['access_token'])
        return response, 200
    
@auth_bp.post('/tmp_token')
def check_tmp_token():
    #Get tmp token to check if ok and still valid or not
    result = auth_service.handle_check_tmp_token()
    return jsonify({'data': result['data']}), 200

@auth_bp.get('/logout')
def logout():
    res = jsonify({'msg': 'logout successfully'})
    unset_jwt_cookies(res)
    return res