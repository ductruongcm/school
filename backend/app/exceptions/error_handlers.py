from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from flask import request, jsonify, g
from .exceptions import Errors_with_log, CustomException, Errors, NotFound_Exception, DuplicateException
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
    
    @app.errorhandler(DuplicateException)
    def handle_duplicate_exception(e):
        db.session.rollback()
        action = f'{request.method} {request.path}'
        if getattr(g, 'with_log', False):
            error = Errors_with_log(e, db, action).error_409()
        else:
            error = Errors(e).error_409()
        print('traceback', traceback.format_exc())
        return jsonify(error), 409
    
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
    
    @app.errorhandler(IntegrityError)
    def handler_integrity_error(e):
        db.session.rollback()

        msg = str(e.orig)
        if "uq_student_lesson_period" in msg:
            error_msg = "Bảng điểm của học kỳ này đã tạo rồi!"

            return jsonify({'msg': error_msg}), 400


