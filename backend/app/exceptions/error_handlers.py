from pydantic import ValidationError
from flask import request, jsonify, g
from .exceptions import Errors_with_log, CustomException, Errors, NotFound_Exception
import traceback

def register_error_handler_with_log(app, db):
    @app.errorhandler(ValidationError)
    def handler_validation__error(e):
        db.session.rollback()
        action = f'{request.method} {request.path}'

        if getattr(g, 'with_log', False):
            error = Errors_with_log(e, db, action).error_422()
        else:
            error = Errors(e).error_422()
        print('traceback', traceback.format_exc())
        return jsonify(error), 422
    
    @app.errorhandler(CustomException)
    def handler_custom_exception(e):
        db.session.rollback()
        action = f'{request.method} {request.path}'

        if getattr(g, 'with_log', False):
            error = Errors_with_log(e, db, action).error_400()
        else:
            error = Errors(e).error_400()
        print('traceback', traceback.format_exc())
        return jsonify(error), 400
    
    @app.errorhandler(NotFound_Exception)
    def handler_not_found_exception(e):
        db.session.rollback()
        action = f'{request.method} {request.path}'

        if getattr(g, 'with_log', False):
            error = Errors_with_log(e, db, action).error_404()
        else:
            error = Errors(e).error_404()
        print('traceback', traceback.format_exc())
        return jsonify(error), 404

    @app.errorhandler(Exception)
    def handler_unexpected_error(e):
        db.session.rollback()
        action = f'{request.method} {request.path}'

        if getattr(g, 'with_log', False):
            error = Errors_with_log(e, db, action).error_500()
        else:
            error = Errors(e).error_500()
            
        print('traceback', traceback.format_exc())
        return jsonify(error), 500
    


