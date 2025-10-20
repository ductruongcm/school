from app.models import Audit_logs
from datetime import datetime
from sqlalchemy import func
import math
from .base import BaseRepo

class AuditRepo(BaseRepo):
    def add_log(self, data: dict):
        # IP, username, action, status, info
        self.db.session.add(Audit_logs(**data))

    def show_log(self, data:dict):   
        fields = self.filter_context('username', 'action', 'status', 'start_date', 'end_date', 'page', context=data)                                                                    
        query = self.db.session.query(Audit_logs.client_ip,
                                 Audit_logs.username,
                                 Audit_logs.action,
                                 Audit_logs.datetime,
                                 Audit_logs.status,
                                 Audit_logs.info)
        if fields['username']:
            query = query.filter(Audit_logs.username.ilike(f'%{fields['username']}%'))
        if fields['action']:
            query = query.filter(Audit_logs.action.ilike(f'%{fields['action']}%'))
        if fields['status']:
            query = query.filter(Audit_logs.status.ilike(f'%{fields['status']}%'))
        if not fields['start_date'] and not fields['end_date']:
            today = datetime.utcnow().date()
            query = query.filter(func.date(Audit_logs.datetime) == today)
        elif fields['start_date'] and fields['end_date']:
            query = query.filter(func.date(Audit_logs.datetime).between(fields['start_date'], fields['end_date']))
        elif fields['start_date']:
            query = query.filter(func.date(Audit_logs.datetime) >= fields['start_date'])
        elif fields['end_date']:
            query = query.filter(func.date(Audit_logs.datetime) <= fields['end_date'])

        all_records = query.count()
        limit = 25
        total_pages = math.ceil(all_records / limit) if all_records > limit else 1
        offset = (fields['page'] - 1) * limit
        query = query.order_by(Audit_logs.datetime).limit(limit).offset(offset).all()
        keys = ['client_ip', 'username', 'action', 'datetime', 'status', 'info']
        return {'data': [dict(zip(keys, values)) for values in query],
                'page': fields['page'],
                'total_pages': total_pages}
    