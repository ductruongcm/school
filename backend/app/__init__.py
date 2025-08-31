from flask import Flask
from app.extensions import db, lm, jwt
from configs import Configs
from app.routes import routes

def launch():
    app = Flask(__name__)
    app.config.from_object(Configs)
    db.init_app(app)
    lm.init_app(app)
    jwt.init_app(app)
    for route in routes:
        app.register_blueprint(route)
    return app