from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter, util
from redis import Redis

db = SQLAlchemy()
jwt = JWTManager()
lm = Limiter(key_func = util.get_remote_address, storage_uri = "redis://localhost:6379", )