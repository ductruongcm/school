from app.services import UserService, AuthService
from flask_jwt_extended import get_jwt_identity
from flask import request

class UsersController:
    @staticmethod
    def show_user():
        data = request.args.to_dict()
        result = UserService.handle_show_user(data)
        return result

    @staticmethod
    def show_user_info():
        data = request.args.to_dict()
        result = UserService.handle_show_user_info(data)
        result['username'] = data.get('username')
        return result
    
    @staticmethod
    def update_info():
        data = request.get_json()
        username = get_jwt_identity()
        result = UserService.handle_update_user_info(data)
        result['username'] = username
        return result
    
    @staticmethod
    def reset_password():
        data = request.get_json()
        username = get_jwt_identity()
        result = AuthService.handle_reset_password(username, data)
        return result

class AuthController:
    @staticmethod
    def register():
        data = request.get_json()
        result = AuthService.handle_register(data)
        return result

    @staticmethod
    def login():
        data = request.get_json()
        result = AuthService.handle_login(data)
        result['username'] = data.get('username')
        return result
    
    @staticmethod
    def refresh_token():
        #Get username to get info for new access token
        username = get_jwt_identity()
        result = AuthService.handle_refresh_token(username)
        result['username'] = username
        return result

    @staticmethod
    def check_tmp_token():
        #Get tmp token to check if ok and still valid or not
        data = request.get_json()
        result = AuthService.handle_check_tmp_token(data)
        return result

    @staticmethod
    def set_password():
        data = request.get_json()
        result = AuthService.handle_set_password(data)
        result['user_id'] = data.get('id')
        return result