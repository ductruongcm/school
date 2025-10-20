from flask import jsonify
from app.repositories import AuditRepo
from app.utils import get_client_ip
from flask_jwt_extended import get_jwt_identity

class CustomException(Exception):
    def __init__(self, message):
        self.message = message

class NotFound_Exception(Exception):
    def __init__(self, message):
        self.message = message

class Errors:
    def __init__(self, message):
        self.message = message

    def error_400(self):
        return {'status': 'Logic_error', 'msg': str(self.message)} 
    
    def error_422(self):
        try:
            errors = self.message.errors()
            msgs = []
            for err in errors:
                msg = err['msg']
                if msg.lower().startswith('value error,'):
                    msg = msg.split(',', 1)[1].strip()
                msgs.append(msg)
            msg = '; '.join(msgs)

        except Exception:
            msg = str(self.message)

        return {'status': 'Validation_error', 'msg': msg}
    
    def error_404(self):
        return {'status': '404_error', 'msg': f'{str(self.message)}'}
    
    def error_500(self):
        return {'status': 'Unexpected_error', 'msg': f'{str(self.message)}'}
    
class Errors_with_log(CustomException):
    def __init__(self, message, db, action):
        super().__init__(message)
        self.db = db
        self.repo = AuditRepo(db)
        try:
            username = get_jwt_identity() 
        except:
            username = None
        self.log = {'client_ip': get_client_ip(),
                    'username': username,
                    'action': action,
                    'status': 'Failed',
                    'info': str(self.message)}

    def _log(self):
        self.repo.add_log(self.log)
        self.db.session.commit()

    def error_400(self):
        self._log()
        return {'status': 'Logic_error', 'msg': str(self.message)}
    
    def error_422(self):
        try:
            errors = self.message.errors()
            msgs = []
            for err in errors:
                msg = err['msg']
                if msg.lower().startswith('value error,'):
                    msg = msg.split(',', 1)[1].strip()
                msgs.append(msg)
            msg = '; '.join(msgs)

        except Exception:
            msg = str(self.message)

        self._log
        return {'status': 'Validation_error', 'msg': msg}
    
    def error_404(self):
        self._log()
        return {'status': '404_error', 'msg': f'{str(self.message)}'}
    
    def error_500(self):
        self._log()
        return {'status': 'Unexpected_error', 'msg': f'{str(self.message)}'}
    




# def error_422(exc: ValidationError):
#     errors = exc.errors()

#     for err in errors:
#         msg = err['msg']
#         if msg.lower().startswith('value error,'):
#             msg = msg.split(',', 1)[1].strip()
#     return {'status': 'Validation_error', 'msg': msg}    

# def return_with_data(keys, result):
#     return {'status': 'Success',
#             'data': [dict(zip(keys, values)) for values in result]}

def error_show_return(result):   
    status = result['status'] 
    if status == 'Logic_error':
        return jsonify({'msg': result['msg']}), 400
    
    elif status == 'DB_error':
        return jsonify({'msg': result['msg']}), 500
    
    elif status == 'Validation_error':
        return jsonify({'msg': result['msg']}), 422 
    
    return
    