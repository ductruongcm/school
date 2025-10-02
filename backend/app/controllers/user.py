from app.services import User_service
from flask import request

class User_controller:
    @staticmethod
    def show_user_info():
        data = request.args.to_dict()
        result = User_service.handle_show_user_info(data)
        return result
