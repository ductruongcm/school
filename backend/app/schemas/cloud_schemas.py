from app.extensions import db
from datetime import datetime
# from app.schemas import Class_room

class Cloud(db.Model):
    __tablename__ = 'cloud'
    id = db.Column(db.Integer, primary_key = True)
    class_room_id = db.Column(db.Integer, db.ForeignKey('class_room.id', ondelete = 'CASCADE'))
    folder = db.Column(db.String, nullable = False)
    filename = db.Column(db.String, nullable = False)
    filetype = db.Column(db.String, nullable = False)
    filesize = db.Column(db.String, nullable = False)
    upload_at = db.Column(db.DateTime, default = datetime.utcnow)
    upload_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete = 'CASCADE'))
    status = db.Column(db.Boolean, default = True)
    class_room = db.relationship('Class_room', back_populates = 'cloud', lazy = True)
    users = db.relationship('Users', back_populates = 'cloud', lazy = True)


   