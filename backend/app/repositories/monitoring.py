from app.models import Monitoring
from datetime import datetime
from sqlalchemy import func
import math
from app.extensions import db

class Monitoring_repo:
    def __init__(self, username, action, status):
        from app.utils import get_client_ip
        self.ip = get_client_ip()
        self.username = username
        self.action = action
        self.status = status

    def add_monitoring(self, info):
        db.session.add(Monitoring(client_ip = self.ip, 
                                  username = self.username, 
                                  action = self.action, 
                                  status = self.status, 
                                  info = info))

    def show_monitoring(self, start_date, end_date, page):                                                                                              
        query = db.session.query(Monitoring.client_ip,
                                 Monitoring.username,
                                 Monitoring.action,
                                 Monitoring.datetime,
                                 Monitoring.status,
                                 Monitoring.info)
        if self.username:
            query = query.filter(Monitoring.username.ilike(f'%{self.username}%'))
        if self.action:
            query = query.filter(Monitoring.action.ilike(f'%{self.action}%'))
        if self.status:
            query = query.filter(Monitoring.status.ilike(f'%{self.status}%'))
        if not start_date and not end_date:
            today = datetime.utcnow().date()
            query = query.filter(func.date(Monitoring.datetime) == today)
        elif start_date and end_date:
            query = query.filter(func.date(Monitoring.datetime).between(start_date, end_date))
        elif start_date:
            query = query.filter(func.date(Monitoring.datetime) >= start_date)
        elif end_date:
            query = query.filter(func.date(Monitoring.datetime) <= end_date)

        all_records = query.count()
        limit = 25
        total_pages = math.ceil(all_records / limit) if all_records > limit else 1
        offset = (page - 1) * limit
        query = query.order_by(Monitoring.datetime).limit(limit).offset(offset).all()
        keys = ['client_ip', 'username', 'action', 'datetime', 'status', 'info']

        return {'data': [dict(zip(keys, values)) for values in query],
                'page': page,
                'total_pages': total_pages}
    