from flask import request
from app.services import MonitoringService

class MonitoringController:
    @staticmethod
    def show_monitoring():
        data = request.args.to_dict()
        result = MonitoringService.handle_show_monitoring(data)
        return result