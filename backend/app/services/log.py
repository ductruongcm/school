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
        self.user_validation.validate_user_id(data)
        self.activity_log_repo.add_activity_log(data)