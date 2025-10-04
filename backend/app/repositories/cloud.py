from app.extensions import db
from app.models import Class_room, Cloud, Users
from datetime import datetime

class CloudRepositories:
    @staticmethod
    def upload(class_room_id, folder, file_name, file_type, file_size, user_id):
        db.session.add(Cloud(class_room_id = class_room_id,
                            folder = folder, 
                            filename = file_name,
                            filetype = file_type,
                            filesize = file_size,
                            upload_by = user_id))
    
    @staticmethod
    def check_existing_file(class_room_id, folder, file_name):
        return Cloud.query.filter(Cloud.class_room_id == class_room_id, Cloud.folder == folder, Cloud.filename == file_name).first()
    
    @staticmethod
    def show_folder(class_room_id):
        query = db.session.query(Cloud.folder)
        
        if class_room_id:
            query = query.filter(Cloud.class_room_id == class_room_id)
        return [data.folder for data in query.all()]
    
    @staticmethod
    def show_file(class_room_id, folder):
        return db.session.query(Cloud.id,
                                Cloud.filename,
                                Cloud.filetype,
                                Cloud.filesize,
                                Cloud.upload_at,
                                Users.username,
                                Cloud.file_status
                                ).join(Users).filter(Cloud.class_room_id == class_room_id, Cloud.folder == folder).all()
    
    @staticmethod
    def get_file_by_id(id):
        return db.session.query(Cloud.id, Class_room.class_room, Cloud.folder, Cloud.filename).join(Class_room).filter(Cloud.id == id).first()
    
    @staticmethod
    def delete_file(id):
        Cloud.query.filter(Cloud.id == id).delete(synchronize_session = False)

    @staticmethod
    def update_file(id):
        return Cloud.query.filter(Cloud.id == id).first()