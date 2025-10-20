from flask import request, g
from functools import wraps

def validate_input(schema):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
                raw = request.args.to_dict() or request.get_json()
                if isinstance(raw, list): 
                    validated = [schema(**i).model_dump() for i in raw]
                else:
                    validated = schema(**raw).model_dump()
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
                