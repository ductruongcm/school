from flask import Flask
from app.extensions import db, lm, jwt, cors
from configs import Configs
from app.routes import routes

def launch():
    app = Flask(__name__)
    app.config.from_object(Configs)
    db.init_app(app)
    lm.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, supports_credentials = True, origins = ['http://localhost:5173'])
    for route in routes:
        app.register_blueprint(route)
    return app