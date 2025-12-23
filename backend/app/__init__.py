from flask import Flask
from .extensions import db, lm, jwt, cors, migrate
from configs import Configs
from .routes import routes
from .exceptions import register_error_handler_with_log

def launch():
    global celery
    app = Flask(__name__)
    app.config.from_object(Configs)

    db.init_app(app)
    lm.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, origins = ['http://localhost:5173'], supports_credentials = True, max_age=3600)

    for route in routes: 
        app.register_blueprint(route)
    
    register_error_handler_with_log(app, db)

    return app