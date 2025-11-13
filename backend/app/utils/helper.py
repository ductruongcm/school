from flask import request, g
from functools import wraps
from app.exceptions import CustomException

def validate_input(schema):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
                raw = request.args.to_dict() or request.get_json()
                if not raw:
                    raise CustomException('Không có dữ liệu đầu vào!')
                if isinstance(raw, list): 
                    validated = [schema(**i).model_dump(exclude_unset = True) for i in raw]
                else:
                    validated = schema(**raw).model_dump(exclude_unset = True)
                return fn(*args, validated_data = validated, **kwargs)
        return wrapper
    return decorator

def with_log(enable = True):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            g.with_log = enable
            return fn(*args, **kwargs)
        return wrapper
    return decorator
                