from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter, util
from flask_cors import CORS
from flask_mail import Mail
from flask_migrate import Migrate


db = SQLAlchemy()
jwt = JWTManager()
lm = Limiter(key_func = util.get_remote_address, storage_uri = "redis://localhost:6379", )
cors = CORS()
mail = Mail()
migrate = Migrate()
