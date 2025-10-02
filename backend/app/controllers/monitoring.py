from flask import request
from app.services import Monitoring_service

class Monitoring_controller:
    @staticmethod
    def show_monitoring():
        data = request.args.to_dict()
        result = Monitoring_service.handle_show_monitoring(data)
        return result