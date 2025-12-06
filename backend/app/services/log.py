from .validation import User_Validation

class AuditLog_Service:
    def __init__(self, db, repo):
        self.repo = repo(db)

    def handle_show_logs(self, data):
        result = self.repo.show_log(data)
        return result
        
class ActivityLog_Service:
    def __init__(self, db, repo):
        self.repo = repo(db)
        self.activity_log_repo = self.repo.activity_log
        self.user_validation = User_Validation(db, repo)

    def handle_record_activity_log(self, data):
        #check user id
        self.activity_log_repo.add_activity_log(data)

    def handle_show_activity_logs(self, data, username):
        if data['role'] == 'Teacher':
            data['username'] = username

        result = self.activity_log_repo.show_activity_log(data)
        
        return result
