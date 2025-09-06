from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import lm, util
from app.routes.user import db_user_utils
from app.utils import utils
from werkzeug.security import generate_password_hash


user_bp = Blueprint('user_bp', __name__, url_prefix = '/api/user')

@user_bp.post('/update_info')
@lm.limit("5 per minute", key_func = util.get_remote_address)
@jwt_required()
def update_info():
    print(request.cookies)
    data = request.get_json()
    new_username = data.get('username')
    new_email = data.get('email')
    username = get_jwt_identity()
    error = utils.errors(username = new_username, email = new_email)
    if error:
        return jsonify({'msg': error}), 400
    db_user_utils.info_update(data, username)
    return jsonify({'msg': 'Cập nhật thành công!!'}), 200

@user_bp.put('/reset_password')
@jwt_required()
@lm.limit("5 per minute", key_func = util.get_remote_address)
def reset_password():
    username = get_jwt_identity()
    password = request.get_json()['password'].strip()
    re_password = request.get_json()['re_password'].strip()
    errors = utils.password_validates(password, re_password)
    if errors:
        return jsonify({'msg': errors}), 400
    hashed_password = generate_password_hash(password)
    db_user_utils.reset_password(username, hashed_password)
    return jsonify({'msg': 'Đổi mật khẩu thành công'}), 200
