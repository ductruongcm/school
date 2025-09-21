from app.utils.monitoring_utils import get_client_ip
from app.schemas import Monitoring
from datetime import datetime, time
from sqlalchemy import func
import math
from app.extensions import db

def db_record_log(username, action, status , info):
    ip = get_client_ip()
    new_log = Monitoring(client_ip = ip, 
                         username = username, 
                         action = action, 
                         status = status, 
                         info = info)
   
    db.session.add(new_log)
    db.session.commit()

def db_show_monitoring(ip = None, username = None, action = None, start_date = None, end_date = None, status = None, info = None, page = None):
    
    query = db.session.query(Monitoring.client_ip,
                            Monitoring.username,
                            Monitoring.action,
                            Monitoring.datetime,
                            Monitoring.status,
                            Monitoring.info)

    if ip:
        query = query.filter(Monitoring.client_ip.like(f'%{ip}%'))
    if username:
        query = query.filter(Monitoring.username.ilike(f'%{username}%'))
    if action:
        query = query.filter(Monitoring.action.ilike(f'%{action}%'))
    if status:
        query = query.filter(Monitoring.status.ilike(f'%{status}%'))
    if info:
        query = query.filter(Monitoring.info.ilike(f'%{info}%'))
    if not start_date and not end_date:
        today = datetime.utcnow().date()
        query = query.filter(func.date(Monitoring.datetime) == today)
    elif start_date and end_date:
        query = query.filter(func.date(Monitoring.datetime).between(start_date, end_date))
    elif start_date:
        query = query.filter(func.date(Monitoring.datetime) >= start_date)
    elif end_date:
        query = query.filter(func.date(Monitoring.datetime) <= end_date)

    #Đếm tổng số dòng 
    total_records = query.count()
    limit = 25
    #làm tròn lên số page để tính tổng số page
    total_pages = math.ceil(total_records / limit) if total_records > 0 else 1
   
    offset = (page - 1)*limit
    
    rows = query.order_by(Monitoring.datetime).limit(limit).offset(offset).all()
    keys = ['client_ip', 'username', 'action', 'datetime', 'status', 'info']

    return {'data': [dict(zip(keys, row)) for row in rows],
            'page': page,
            'limit': limit,
            'total_pages': total_pages} 