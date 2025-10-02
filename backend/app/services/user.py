from app.schemas import Register, ValidationError, Login, SetPassword, UserSchemas
from app.utils import  error_422, error_400, Password_helpers
from app.extensions import db
from app.repositories import User_repo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta

class Auth_service:
    @staticmethod
    def handle_login(data):
        try:
            data_login = Login(**data)

        except ValidationError as e:
            return error_422(e)
        
        user = User_repo.get_user(data_login.username)
        if not user:
            return {'status': 'Logic_error', 'msg': 'Sai tên đăng nhập hoặc không đúng mật khẩu!'}
        
        if not check_password_hash(user.password, data_login.password):
            return {'status': 'Logic_error', 'msg': 'Sai tên đăng nhập hoặc không đúng mật khẩu!'}
        
        role = user.role
        user_id = user.id

        access_token = create_access_token(identity = data_login.username, 
                                           expires_delta = timedelta(minutes = 15), 
                                           additional_claims = {'role': role, 
                                                                'id': user_id})
        
        refresh_token = create_refresh_token(identity = data_login.username, 
                                             expires_delta = timedelta(hours = 10), 
                                             additional_claims = {'role': role,
                                                                  'id': user_id})
        return {'status': True, 
                'access_token': access_token, 
                'refresh_token': refresh_token,
                'role': role,
                'id': user_id}
    
    @staticmethod
    def handle_register(data):
        try:
            register_data = Register(**data)
        
        except ValidationError as e:
            return error_422(e)
         
        logic_error = Password_helpers().validate(register_data.password, register_data.repassword)
        if logic_error:
            return error_400(logic_error)
        
        elif User_repo.get_user(register_data.username):
            return {'status': 'Logic_error', 'msg': 'Username này đã được sử dụng!'}
        
        try:
            hashed_password = generate_password_hash(register_data.password)
            User_repo.add_user(register_data.username, hashed_password, register_data.name)
            db.session.commit()       
            return {'status': 'ok', 'msg': 'Registration success', 'username': register_data.username}
            
        except Exception as e:
            db.session.rollback()
            return {'status': 'DB_error', 'msg': f'DB_error: {e}', 'username': register_data.username}
        
    @staticmethod
    def handle_refresh_token(username):
        user = User_repo.get_user(username)
        if not user:
            return {'status': False, 'msg': 'User không tồn tại'}
        
        role = user.role
        id = user.id

        access_token = create_access_token(identity = username, 
                                           expires_delta = timedelta(minutes = 15), 
                                           additional_claims = {'role': role, 'id': id})
        return {'status': True, 'access_token': access_token, 'role': role, 'id': id}
    
    @staticmethod
    def handle_check_tmp_token(data):
        token = User_repo.get_tmp_token(data)
        if token:
            return {'status': 'ok', 'msg': 'Token hợp lệ!'}
        else:
            return {'status': 'DB_error', 'msg': 'Token không hợp lệ!'}
    
class User_service:
    @staticmethod
    def handle_show_user(data):
        try:
            search_data = UserSchemas.UserShowSchema(**data)

        except ValidationError as e:
            return error_422(e)
        
        try:
            result = User_repo.show_user(search_data.username, search_data.role, search_data.page)
            if result:
                return {'status': 'ok', 'data': result}
            
            else:
                return {'status': 'Logic_error', 'msg': 'Không tìm thấy dữ liệu'}
            
        except Exception as e:
            return {'status': 'DB_error', 'msg': f'DB_error: {str(e)}'}

    @staticmethod
    def handle_show_user_info(data):
        result = User_repo.show_user_info(data['id'], data['role'])
        keys = ['name', 'email', 'tel', 'add']

        return [dict(zip(keys, values)) for values in result][0]

    @staticmethod
    def handle_update_user_info(data):
        try:
            update_data = UserSchemas.UserInfoUpdateSchema(**data)

        except ValidationError as e:
            return error_422(e)
        
        try:
            User_repo.update_user_info(update_data.id, 
                                        update_data.name, 
                                        update_data.username, 
                                        update_data.email, 
                                        update_data.tel, 
                                        update_data.add)
            db.session.commit()
            return {'status': 'ok', 'msg': 'Cập nhật thông tin cá nhân thành công!'}
        
        except Exception as e:
            db.session.rollback()
            return {'status': 'DB_error', 'msg': f'DB_error: {str(e)}'}
        
    @staticmethod
    def handle_set_password(data):
        try:
            set_password_data = SetPassword(**data)
            
        except ValidationError as e:
            return error_422(e)
            
        try:
            token = User_repo.get_tmp_token(set_password_data.token)
            if token:
                hashed_password = generate_password_hash(data['password'])
                User_repo.set_password(token.user_id, hashed_password)
                db.session.commit()
                return {'status': 'ok', 'msg': 'Thiết lập mật khẩu thành công'}
            
            else:
                return {'status': 'Logic_error', 'msg': 'Token không hợp lệ!'}
        
        except Exception as e:
            return {'status': 'DB_error', 'msg': f'DB_error: {str(e)}'}
            

                
    
