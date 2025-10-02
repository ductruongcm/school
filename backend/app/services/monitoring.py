from app.schemas import MonitoringShowSchema, ValidationError
from app.repositories import Monitoring_repo
from app.utils import error_422
from app.extensions import db

class Monitoring_service:
    @staticmethod
    def handle_add_monitoring(username, action, status, info):
        repo = Monitoring_repo(username, action, status)
        repo.add_monitoring(info)
        db.session.commit()

    @staticmethod
    def handle_show_monitoring(data):
        try:
            search_data = MonitoringShowSchema(**data)
        except ValidationError as e:
            return error_422(e)
        
        try:
            repo = Monitoring_repo(search_data.username, search_data.action, search_data.status)
            result = repo.show_monitoring(search_data.start_date, search_data.end_date, search_data.page)
            if result:
                return {'status': 'ok', 'data': result}
            
            else:
                return {'status': 'Logic_error', 'msg': 'Không tìm thấy dữ liệu!'}
            
        except Exception as e:
            return {'status': 'DB_error', 'msg': f'DB_error: {str(e)}'}