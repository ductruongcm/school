from app.models import Audit_logs, Activity_Log, Users
from datetime import datetime, date
import math
from .base import BaseRepo

class AuditLogRepo(BaseRepo):
    def add_audit_log(self, data: dict):
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
            start = datetime.combine(today, datetime.min.time())
            end = datetime.combine(today, datetime.max.time())
            query = query.filter(Audit_logs.datetime.between(start, end))

        elif fields['start_date'] and fields['end_date']:
            start = datetime.combine(date.fromisoformat(fields['start_date']), datetime.min.time())
            end = datetime.combine(date.fromisoformat(fields['end_date']), datetime.max.time())
            query = query.filter(Audit_logs.datetime.between(start, end))

        elif fields['start_date']:
            start = datetime.combine(date.fromisoformat(fields['start_date']), datetime.min.time())
            query = query.filter(Audit_logs.datetime >= start)

        elif fields['end_date']:
            end = datetime.combine(date.fromisoformat(fields['end_date']), datetime.max.time())
            query = query.filter(Audit_logs.datetime <= end)

        all_records = query.count()
        limit = 25
        total_pages = math.ceil(all_records / limit) if all_records > limit else 1
        offset = (fields['page'] - 1) * limit
        query = query.order_by(Audit_logs.datetime).limit(limit).offset(offset).all()
        keys = ['client_ip', 'username', 'action', 'datetime', 'status', 'info']
        return {'data': [dict(zip(keys, values)) for values in query],
                'page': fields['page'],
                'total_pages': total_pages}

class ActivityLogRepo(BaseRepo):
    def add_activity_log(self, data):
        self.db.session.add(Activity_Log(**data))

    def show_activity_log(self, data):
        query = self.db.session.query(Users.username,
                                      Activity_Log.module,
                                      Activity_Log.action,
                                      Activity_Log.target_id,
                                      Activity_Log.detail,
                                      Activity_Log.created_at).join(Users.activity_log)
        
        if data.get('username'):
            query = query.filter(Users.username.ilike(f'%{data['username']}%'))

        if data.get('action'):
            query = query.filter(Activity_Log.action.ilike(f'%{data['action']}%'))

        if data.get('module'):
            query = query.filter(Activity_Log.module.ilike(f'%{data['module']}%'))

        if data.get('start_date') and data.get('end_date'):
            start = datetime.combine(date.fromisoformat(data['start_date']), datetime.min.time())
            end = datetime.combine(date.fromisoformat(data['end_date']), datetime.max.time())
            query = query.filter(Activity_Log.created_at.between(start, end))

        elif data.get('start_date'):
            start = datetime.combine(date.fromisoformat(data['start_date']), datetime.min.time())
            query = query.filter(Activity_Log.created_at >= start) 

        elif data.get('end_date'):
            end = datetime.combine(date.fromisoformat(data['end_date']), datetime.max.time())
            query = query.filter(Activity_Log.created_at <= end)

        elif not data.get('start_date') and not data.get('end_date'):
            today = datetime.utcnow().date()
            start = datetime.combine(today, datetime.min.time())
            end = datetime.combine(today, datetime.max.time())
            query = query.filter(Activity_Log.created_at.between(start, end))

        total_records = query.count()

        limit = 15
        total_pages = math.ceil(total_records/limit) if total_records > limit else 1
        offset = (data['page'] - 1)*limit 
        query = query.order_by(Activity_Log.created_at).limit(limit).offset(offset).all()

        keys = ['username', 'module', 'action', 'target_id', 'detail', 'created_at']

        return {'data': [dict(zip(keys, values)) for values in query],
                'total_pages': total_pages,
                'page': data['page']}
        