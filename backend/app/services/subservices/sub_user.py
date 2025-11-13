from app.exceptions import NotFound_Exception

class User_Subservices:
    def __init__(self, repo, teacher_repo, student_repo):
        self.repo = repo
        self.teacher_repo = teacher_repo
        self.student_repo = student_repo

    def check_user(self, data):
        user = self.repo.get_user_by_id(data)
        if not user:
            raise NotFound_Exception('Không tìm thấy User ID!')
        return user
        
    def check_user_info(self, data):
        user_info = self.repo.get_user_info(data)
        if not user_info:
            raise NotFound_Exception('Không tìm thấy thông tin!')
        
        return user_info
    
    def check_tmp_token_by_user_id(self, data):
        tmp_token = self.repo.get_tmp_token_by_user_id(data)
        if not tmp_token:
            raise NotFound_Exception('Không tìm thấy tmp_Token!')
        return tmp_token
    
    
