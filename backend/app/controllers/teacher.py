from flask import request
from flask_jwt_extended import get_jwt_identity
from app.services import TeacherService

class TeacherController:
    @staticmethod
    def add_teacher():
        username = get_jwt_identity()
        data = request.get_json()
        result = TeacherService.handle_add_teacher(data)
        result['username'] = username
        result['name'] = data.get('name')
        return result
    
    @staticmethod
    def show_teacher():
        data = request.args.to_dict()
        result = TeacherService.handle_show_teacher(data)
        return result
    
    @staticmethod
    def update_teacher_info():
        data = request.get_json()
        result = TeacherService.handle_update_info(data)
        return result
