from pydantic import ValidationError
from flask import jsonify

def error_422(exc: ValidationError):
    errors = exc.errors()

    for err in errors:
        msg = err['msg']
        if msg.lower().startswith('value error,'):
            msg = msg.split(',', 1)[1].strip()
    return {'status': 'Validation_error', 'msg': msg}    

def error_400(helper_error: list[dict]):
    return {'status': 'Logic_error', 'msg': helper_error}

def error_show_return(result):
    if result['status'] == 'Validation_error':
        return jsonify({'msg': result['msg']}), 422
       
    elif result['status'] == 'Logic_error':
        return jsonify({'msg': result['msg']}), 400
    
    elif result['status'] == 'DB_error':
        return jsonify({'msg': result['msg']}), 500
