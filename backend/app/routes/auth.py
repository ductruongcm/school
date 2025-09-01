from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt, jwt_required

auth_bp = Blueprint('auth_bp', __name__, url_prefix = '/api/auth')

@auth_bp.get('/register')
def register():
    pass

@auth_bp.get('/user_info')
@jwt_required()
def user_info():
    username = get_jwt_identity()
    role = get_jwt().get('role') 
    return jsonify({'username': username, 'role': role})
