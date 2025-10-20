from app.extensions import db
from datetime import datetime

class Audit_logs(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key = True)
    client_ip = db.Column(db.String(12), nullable = False)
    username = db.Column(db.String(20))
    action = db.Column(db.String(30), nullable = False)
    status = db.Column(db.String(8), nullable = False)
    info = db.Column(db.String)
    datetime = db.Column(db.DateTime, default = datetime.utcnow)
 