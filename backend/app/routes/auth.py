from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt, jwt_required, create_access_token, set_access_cookies
from datetime import timedelta

auth_bp = Blueprint('auth_bp', __name__, url_prefix = '/api/auth')

@auth_bp.get('/register')
def register():
    pass

@auth_bp.get('/user_info')
@jwt_required()
def user_info():
    username = get_jwt_identity()
    role = get_jwt().get('role') 
    return jsonify({'username': username, 'role': role}), 200

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