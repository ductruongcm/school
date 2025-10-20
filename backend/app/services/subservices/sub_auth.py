from werkzeug.security import check_password_hash

class AuthSub_service:
    def __init__(self, repo):
        self.repo = repo

    def check_user(self, data):   
        user = self.repo.get_user(data)
        if check_password_hash(user.password, data.get('password')):
            return user
        

