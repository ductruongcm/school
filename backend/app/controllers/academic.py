from flask import request
from app.services import Class_room_service, Academic_service
from flask_jwt_extended import get_jwt_identity

class Class_room_controller:
    @staticmethod
    def add_class_room(): 
        data = request.get_json()
        result = Class_room_service.handle_add_class_room(data)
        result['username'] = get_jwt_identity()
        result['class_room'] = data.get('class_room')
        return result
    
    @staticmethod
    def show_class_room():
        data = request.args.to_dict()
        result = Class_room_service.handle_show_class_room(data)
        return result
    
    @staticmethod
    def show_teach_room():
        year = request.get_json()
        username = get_jwt_identity()
        result = Class_room_service.handle_show_teach_rooom(year, username)
        return result

class Academic_controller:
    class Add_controller:
        @staticmethod
        def add_year():
            data = request.get_json()
            result = Academic_service.handle_add_year(data)
            return result

        @staticmethod
        def add_semester():
            data = request.get_json()
            result = Academic_service.handle_add_semester(data)
            return result

        @staticmethod
        def add_lesson():
            data = request.get_json()
            result = Academic_service.handle_add_lesson(data)
            return result

        @staticmethod
        def add_grade():
            data = request.get_json()
            result = Academic_service.handle_add_grade(data)
            return result
    
    class Show_controller:
        @staticmethod
        def show_year():
            data = request.args.to_dict()
            result = Academic_service.handle_show_year(data)
            return result

        @staticmethod
        def show_semester():
            data = request.args.to_dict()
            result = Academic_service.handle_show_semester(data)
            return result

        @staticmethod
        def show_lesson():
            data = request.args.to_dict()
            result = Academic_service.handle_show_lesson(data)
            return result

        @staticmethod
        def show_grade():
            data = request.args.to_dict()
            result = Academic_service.handle_show_grade(data)
            return result