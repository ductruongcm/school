from app.extensions import db
from app.schemas import Class_room, Cloud, Users
from datetime import datetime

def db_upload(username, file_name, file_size, file_type, class_room):
    class_room_id = Class_room.query.filter(Class_room.class_room == class_room).first().id
    user_id = Users.query.filter(Users.username == username).first().id
    new_cloud = Cloud(class_room_id = class_room_id, 
                      filename = file_name, 
                      filesize = file_size,
                      filetype = file_type,
                      upload_by = user_id,
                      upload_at = datetime.utcnow())
    db.session.add(new_cloud)
    db.session.commit()

def db_show_folder(class_room):
    class_room_id = Class_room.query.filter(Class_room.class_room == class_room).first().id
    data = db.session.query(Cloud.filename, 
                            Cloud.filetype, 
                            Cloud.filesize, 
                            Cloud.upload_at, 
                            Users.username,
                            Cloud.status).join(Users).filter(Cloud.class_room_id == class_room_id).order_by(Cloud.filename).all()

    keys = ['file_name', 'file_type', 'file_size', 'upload_at', 'upload_by', 'status']
    return [dict(zip(keys, value)) for value in data]

def db_hide_file(class_room, file_name):
    class_room_id = Class_room.query.filter(Class_room.class_room == class_room).first().id
    file = Cloud.query.filter(Cloud.class_room_id == class_room_id, Cloud.filename == file_name).first()
    file.status = False
    db.session.commit()

def db_unhide_file(class_room, file_name):
    class_room_id = Class_room.query.filter(Class_room.class_room == class_room).first().id
    file = Cloud.query.filter(Cloud.class_room_id == class_room_id, Cloud.filename == file_name).first()
    file.status = True
    db.session.commit()

def db_delete(class_room, file_name):
    class_room_id = Class_room.query.filter(Class_room.class_room == class_room).first().id
    Cloud.query.filter(Cloud.class_room_id == class_room_id, Cloud.filename == file_name).delete(synchronize_session = False)
    db.session.commit()