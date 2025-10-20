from .base import BaseService
from app.exceptions import Errors

class AuditService(BaseService):
    def __init__(self, db, repo):
        super().__init__(db)
        self.repo = repo(db)

    def handle_show_logs(self, data):
        result = self.repo.show_log(data)
        return result
        
 