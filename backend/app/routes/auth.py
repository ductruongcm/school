from flask import Blueprint, jsonify, make_response
from app.utils import with_log, validate_input
from app.extensions import lm, util, db
from datetime import datetime, timedelta
from app.schemas import Login
from app.services import AuthService, Auth_Workflow
from app.repositories import Repositories
from flask_jwt_extended import jwt_required, set_access_cookies, set_refresh_cookies, unset_jwt_cookies, get_jwt

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/auth')
auth_service = AuthService(db, Repositories)
auth_workflow = Auth_Workflow(db, Repositories)

@auth_bp.post('/login')
@lm.limit("5 per minute", key_func = util.get_remote_address)
@with_log(True)
@validate_input(Login)
def login(validated_data):
    result = auth_workflow.process_login(validated_data)
    response = make_response({'id':result['id'],
                              'username': result['username'],
                              'role': result['role'],
                              'expired_at': datetime.utcnow() + timedelta(minutes=15),
                              'active': result['active_status'],
                              'is_homeroom_teacher': result.get('is_homeroom_teacher'),
                              'homeroom_id': result.get('homeroom_id')})
                
    set_access_cookies(response, result['access_token'])
    set_refresh_cookies(response, result['refresh_token'])

    return response, 201

@auth_bp.post('/refresh_token')
@jwt_required(refresh = True)
def refresh_token():
    # axios.get('url') là đã xác nhận đc refresh token
    # lấy thông tin, tạo mới access token
    # truyền thông tin qua res
    # đính kèm cookie chứa access token  
    result = auth_service.handle_refresh_token({'user_id': get_jwt().get('id'),
                                                'is_homeroom_teacher': get_jwt().get('is_homeroom_teacher'),
                                                'homeroom_id': get_jwt().get('homeroom_id')})
    
    response = make_response({'id': result['id'],
                              'username': result['username'],
                              'role': result['role'],
                              'expired_at': datetime.utcnow() + timedelta(minutes=15),
                              'is_homeroom_teacher': get_jwt().get('is_homeroom_teacher'),
                              'homeroom_id': get_jwt().get('homeroom_id')})
    
    set_access_cookies(response, result['access_token'])
    return response, 201

@auth_bp.get('/logout')
def logout():
    res = jsonify({'msg': 'logout successfully'})
    unset_jwt_cookies(res)
    return res