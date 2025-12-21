from werkzeug.security import generate_password_hash
from app.utils import token_set_password, generate_password
from datetime import datetime, timedelta
from app.tasks import send_email_task
from .validation import User_Validation
from app.exceptions import NotFound_Exception

class UserService:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.user_repo = self.repo.user
        self.user_validation = User_Validation(db, repo)


    def new_student_data_for_user(self, student_code):
        #Create username/password/role
        password = generate_password(length=8)
        user_data = {'username': student_code.lower(),
                    'password': generate_password_hash(password),
                    'tmp_password': password,
                    'role': 'Student'}
        
        return user_data

    def new_teacher_data_for_user(self, data):
        password = generate_password(length=32)
        user_data = {'username': data['username'],
                     'password': generate_password_hash(password),
                     'role': 'Teacher'}
        return user_data

    def handle_add_user(self, data):
        #username, password, role, tmp_password
        self.user_validation.check_dup_username(data)
        user = self.user_repo.insert_user(data)

        return user

    def handle_upsert_tmp_token(self, data):
        tmp_token = generate_password_hash(generate_password(length=32))
        self.user_repo.upsert_tmp_token({'user_id': data['user_id'],
                                         'token': tmp_token})
        
        return tmp_token

    def handle_show_user(self, data):
        if result:= self.user_repo.show_user(data):
            return result
        
    def handle_show_user_info(self, data):
        if data['role'] in ['Teacher', 'admin']:
            result = [self.user_repo.show_teacher_info(data)]
            keys = ['name', 'email', 'tel', 'add']

        elif data['role'] == 'Student':
            result = [self.user_repo.show_student_info(data)]
            keys = ['name', 'tel', 'add']

        return [dict(zip(keys, values)) for values in result][0]
    
    def get_user_by_id(self, data):
        user = self.user_repo.get_user_by_id(data)
        if not user:
            raise NotFound_Exception('Không tìm thấy User ID!')
        return user
    
    def get_user_info_by_id(self, data):
        user_info = self.user_repo.get_user_info(data)
        if not user_info:
            raise NotFound_Exception('Không tìm thấy thông tin!')
        return user_info
    
    def get_tmp_token_by_user(self, data):
        tmp_token = self.user_repo.get_tmp_token_by_user_id(data)
        if not tmp_token:
            raise NotFound_Exception('Không tìm thấy tmp_Token!')
        return tmp_token
    
    def get_user_by_tmp_token(self, data):
        user  = self.user_repo.get_user_by_tmp_token(data)
        if not user:
            raise NotFound_Exception('Không tìm thấy User ID!')
        return user
    
    def handle_check_tmp_token_for_set_password(self, data):
        user_id, name = self.get_user_by_tmp_token(data)

        return {'id': user_id,
                'username': name}
        
    def handle_renew_tmp_token(self, data):
        #Make new tmp token
        #update to Tmp_token
        #Get email in Info and send
        new_tmp_token = generate_password_hash(token_set_password(length = 32))

        tmp_token = self.get_tmp_token_by_user(data)
        tmp_token.token = new_tmp_token
        tmp_token.expire_at = datetime.utcnow() + timedelta(hours = 7)

        user_info = self.get_user_info_by_id(data)

        self.db.session.commit()

        link = f'http://localhost:5173/setpassword?token={new_tmp_token}'
        send_email_task.delay(user_info.email, 'Renew password', f'Click here the following link to renew password: {link}')

        return user_info

    def handle_set_password(self, data):        
        self.auth_subservices.check_password(data)

        user = self.auth_subservices.check_tmp_token(data)
       
        self.user_repo.set_password({'password': generate_password_hash(data['password']), 'user_id': user.user_id})
        self.db.session.commit()
        return user
    


  
        

        


