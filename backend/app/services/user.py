from .subservices.sub_user import User_Subservices
from werkzeug.security import generate_password_hash
from app.utils import token_set_password
from datetime import datetime, timedelta
from app.tasks import send_email_task

class UserService:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.user_subservices = User_Subservices(self.repo)

    def handle_show_user(self, data):
        if result:= self.repo.show_user(data):
            return result
        
    def handle_show_user_info(self, data):
        if data['role'] in ['Teacher', 'admin']:
            result = [self.repo.show_teacher_info(data)]
            keys = ['name', 'email', 'tel', 'add']

        elif data['role'] == 'Student':
            result = [self.repo.show_student_info(data)]
            keys = ['name', 'tel', 'add']

        return [dict(zip(keys, values)) for values in result][0]
    
    def handle_update_user_info(self, data):
        self.repo.update_user_info(data)
        self.db.session.commit()
        return {'status': 'Success', 'msg': 'Đã cập nhật thông tin cá nhân!'}
        
    def handle_reset_password(self, data):
        user = self.user_subservices.check_user(data)

        self.user_subservices.check_password(data)
  
        user.password = generate_password_hash(data['password'])
        self.db.session.commit()
        return user
        
        
    def handle_renew_tmp_token(self, data):
        #Make new tmp token
        #update to Tmp_token
        #Get email in Info and send
        new_tmp_token = generate_password_hash(token_set_password(length = 32))

        tmp_token = self.user_subservices.check_tmp_token_by_user_id(data)
        tmp_token.token = new_tmp_token
        tmp_token.expire_at = datetime.utcnow() + timedelta(hours = 7)

        user_info = self.user_subservices.check_user_info(data)

        self.db.session.commit()

        link = f'http://localhost:5173/setpassword?token={new_tmp_token}'
        send_email_task.delay(user_info.email, 'Renew password', f'Click here the following link to renew password: {link}')

        return user_info

    def handle_check_tmp_token(self, data):
        user = self.user_subservices.check_tmp_token(data)
        return {'id': user.user_id,'username': user.username}
        
    def handle_set_password(self, data):        
        self.user_subservices.check_password(data)

        user = self.user_subservices.check_tmp_token(data)
       
        self.repo.set_password({'hashed_password': generate_password_hash(data['password']), 'id': user.user_id})
        self.db.session.commit()
        return user
        

        


