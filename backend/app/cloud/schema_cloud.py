from app.extensions import db
from datetime import datetime

class Cloud(db.Model):
    __tablename__ = 'cloud'
    id = db.Column(db.Integer, primary_key = True)
    class_room_id = db.Column(db.Integer, db.ForeignKey('class_room.id', ondelete = 'CASCADE'))
    filename = db.Column(db.String, nullable = False)
    filetype = db.Column(db.String, nullable = False)
    filesize = db.Column(db.String, nullable = False)
    upload_at = db.Column(db.DateTime, default = datetime.utcnow)
    upload_by = db.Column(db.String(15), nullable = False)
    status = db.Column(db.Boolean, default = True)
    class_room = db.relationship('Class_room', back_populates = 'cloud', lazy = True)