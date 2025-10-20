from app.extensions import db
from datetime import datetime
from sqlalchemy.orm import validates
import re

class Files(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key = True)
    folder_id = db.Column(db.Integer, db.ForeignKey('teach_class.id', ondelete = 'CASCADE'), nullable = False)
    filename = db.Column(db.String, nullable = False)
    filetype = db.Column(db.String, nullable = False)
    filesize = db.Column(db.String, nullable = False)
    upload_at = db.Column(db.DateTime, default = datetime.utcnow)
    upload_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete = 'CASCADE'), nullable = False)
    file_status = db.Column(db.Boolean, default = True)
    users = db.relationship('Users', back_populates = 'files', lazy = True)
    teach_class = db.relationship('Teach_class', back_populates = 'files', lazy = True)

    @validates('filename')
    def filename_validate(self, key, value):
        if not value:
            raise ValueError('Chưa nhập tên file!')
        
        elif not re.fullmatch(r'[A-Za-z0-9_.]+', value):
            raise ValueError("Thông tin không được chứa số và ký tự đặc biệt!")
        
        return value