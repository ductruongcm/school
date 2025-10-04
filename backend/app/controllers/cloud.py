from app.services import CloudService
from flask import request
from flask_jwt_extended import get_jwt_identity

class CloudController:
    @staticmethod
    def upload():
        data = request.get_json()
        result = CloudService.handle_upload(data)
        return result
    
    @staticmethod
    def show_folder():
        data = request.args.to_dict()
        result = CloudService.handle_show_folder(data)
        return result
    
    @staticmethod
    def show_file():
        data = request.args.to_dict()
        result = CloudService.handle_show_file(data)
        return result
    
    @staticmethod
    def delete_file(id):
        username = get_jwt_identity()
        result = CloudService.handle_delete(id)
        result['username'] = username
        return result