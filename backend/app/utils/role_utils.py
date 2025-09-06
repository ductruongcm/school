from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import jsonify

def required_role(*roles):  
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request(optional = False)
            data = get_jwt()
            role = data.get('role').strip()
            if role not in roles:
                return jsonify({'msg': 'Forbidden: Access denied!'}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator
