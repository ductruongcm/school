from flask import request
from app.services import ClassroomService, AcademicService
from flask_jwt_extended import get_jwt_identity, get_jwt

class ClassroomsController:
    @staticmethod
    def add_class_room(): 
        data = request.get_json()
        result = ClassroomService.handle_add_class_room(data)
        result['username'] = get_jwt_identity()
        result['class_room'] = data.get('class_room')
        return result
    
    @staticmethod
    def show_class_room():
        data = request.args.to_dict()
        result = ClassroomService.handle_show_class_room(data)
        return result
    
    @staticmethod
    def show_teach_room():
        data = request.args.to_dict()
        role = get_jwt().get('role')
        id = get_jwt().get('id')
        result = ClassroomService.handle_show_teach_room(data.get('year'), role, id)
        return result

class AcademicController:
    class Add_controller:
        @staticmethod
        def add_year():
            data = request.get_json()
            result = AcademicService.handle_add_year(data)
            return result

        @staticmethod
        def add_semester():
            data = request.get_json()
            result = AcademicService.handle_add_semester(data)
            return result

        @staticmethod
        def add_lesson():
            data = request.get_json()
            result = AcademicService.handle_add_lesson(data)
            return result

        @staticmethod
        def add_grade():
            data = request.get_json()
            result = AcademicService.handle_add_grade(data)
            return result
    
    class Show_controller:
        @staticmethod
        def show_year():
            data = request.args.to_dict()
            result = AcademicService.handle_show_year(data)
            return result

        @staticmethod
        def show_semester():
            data = request.args.to_dict()
            result = AcademicService.handle_show_semester(data)
            return result

        @staticmethod
        def show_lesson():
            data = request.args.to_dict()
            role = get_jwt().get('role')
            id = get_jwt().get('id')
            result = AcademicService.handle_show_lesson(data, role, id)
            return result

        @staticmethod
        def show_grade():
            data = request.args.to_dict()
            result = AcademicService.handle_show_grade(data)
            return result