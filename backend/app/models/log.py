from app.extensions import db
from datetime import datetime

class Audit_logs(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key = True)
    client_ip = db.Column(db.String(12), nullable = False)
    username = db.Column(db.String(20))
    action = db.Column(db.String(50), nullable = False)
    status = db.Column(db.String(8), nullable = False)
    info = db.Column(db.String)
    datetime = db.Column(db.DateTime, default = datetime.utcnow)
 

class Activity_Log(db.Model):
    __tablename__ = 'activity_log'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete = 'NO ACTION'))
    module = db.Column(db.String(100))
    action = db.Column(db.String(50))
    target_id = db.Column(db.String(50))
    detail = db.Column(db.Text)
    status = db.Column(db.String(20), default = 'SUCCESS')
    created_at = db.Column(db.DateTime, default = datetime.utcnow)
    users = db.relationship('Users', back_populates = 'activity_log', lazy = True)