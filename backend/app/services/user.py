from app.schemas import Register, ValidationError, Login, SetPassword, UserSchemas
from app.utils import  error_422, error_400, Password_helpers, token_set_password, send_set_password_email
from app.extensions import db
from app.repositories import UsersRepositories, TeachersRepositories
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta, datetime
import traceback

class AuthService:
    @staticmethod
    def handle_login(data):
        try:
            data_login = Login(**data)

        except ValidationError as e:
            return error_422(e)
        
        user = UsersRepositories.get_user(data_login.username)
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
        
        elif UsersRepositories.get_user(register_data.username):
            return {'status': 'Logic_error', 'msg': 'Username này đã được sử dụng!'}
        
        try:
            hashed_password = generate_password_hash(register_data.password)
            UsersRepositories.add_user(register_data.username, hashed_password, register_data.name)
            db.session.commit()       
            return {'status': 'ok', 'msg': 'Registration success', 'username': register_data.username}
            
        except Exception as e:
            db.session.rollback()
            return {'status': 'DB_error', 'msg': f'DB_error: {e}', 'username': register_data.username}
        
    @staticmethod
    def handle_refresh_token(username):
        user = UsersRepositories.get_user(username)
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
        token = UsersRepositories.get_tmp_token(data['token'])
        if token:
            return {'status': 'ok', 'msg': 'Token hợp lệ!'}
        else:
            return {'status': 'DB_error', 'msg': 'Token không hợp lệ!'}
        
    @staticmethod
    def handle_set_password(data):
        try:
            set_password_data = SetPassword(**data)
            
        except ValidationError as e:
            return error_422(e)
            
        try:
            token = UsersRepositories.get_tmp_token(set_password_data.token)
            if token:
                hashed_password = generate_password_hash(data['password'])
                UsersRepositories.set_password(token.user_id, hashed_password)
                db.session.commit()
                return {'status': 'ok', 'msg': 'Thiết lập mật khẩu thành công'}
            
            else:
                return {'status': 'Logic_error', 'msg': 'Token không hợp lệ!'}
        
        except Exception as e:
            return {'status': 'DB_error', 'msg': f'DB_error: {str(e)}'}    
        
    @staticmethod
    def handle_reset_password(username, data):
        try:
            reset_password_data = SetPassword(**data)

        except ValidationError as e:
            return error_422(e)
        
        try:
            logic_error = Password_helpers().validate(reset_password_data.repassword, reset_password_data.password)
            if logic_error:
                return error_400(logic_error)
            
            hashed_password = generate_password_hash(reset_password_data.password)
            user = UsersRepositories.get_user(username)
            if user:
                user.password = hashed_password
                db.session.commit()

            return error_400('User không tồn tại!')
        
        except Exception as e:
            print(traceback.format_exc())
            db.session.rollback()
            return {'status': 'DB_error', 'msg': f'{str(e)}'}

    @staticmethod
    def renew_tmp_token(id):
        try:
            user_info = TeachersRepositories.Get_repo.get_teacher_info(id)
            if user_info:
               
                new_tmp_token = generate_password_hash(token_set_password(length=32))
                email = user_info.email
                tmp_token = UsersRepositories.get_tmp_token_by_id(id)
                tmp_token.token = new_tmp_token
                tmp_token.expire_at = datetime.utcnow() + timedelta(hours=7) 
                db.session.commit()
                
                link = f'http://localhost:5173/setpassword?token={new_tmp_token}'
                send_set_password_email(email, 'Renew Password', f'Click here the following link to renew password: {link}')

                
            return error_400('User không tồn tại!')
        
        except Exception as e:
            print(traceback.format_exc())
            db.session.rollback()
            return {'status': 'DB_error', 'msg': f'{str(e)}'}

class UserService:
    @staticmethod
    def handle_show_user(data):
        try:
            search_data = UserSchemas.UserShowSchema(**data)

        except ValidationError as e:
            return error_422(e)
        
        try:
            result = UsersRepositories.show_user(search_data.username, search_data.role, search_data.page)
            if result:
                return {'status': 'ok', 'data': result}
            
            else:
                return {'status': 'Logic_error', 'msg': 'Không tìm thấy dữ liệu'}
            
        except Exception as e:
            return {'status': 'DB_error', 'msg': f'DB_error: {str(e)}'}

    @staticmethod
    def handle_show_user_info(data):
        result = UsersRepositories.show_user_info(data['id'], data['role'])
        keys = ['name', 'email', 'tel', 'add']

        return [dict(zip(keys, values)) for values in result][0]

    @staticmethod
    def handle_update_user_info(data):
        try:
            update_data = UserSchemas.UserInfoUpdateSchema(**data)

        except ValidationError as e:
            return error_422(e)
        
        try:
            UsersRepositories.update_user_info(update_data.id, 
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
        

            

                
    
