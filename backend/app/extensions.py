from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter, util
from flask_cors import CORS
from flask_mail import Mail
from flask_migrate import Migrate
from minio import Minio
from os import getenv
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()
lm = Limiter(key_func = util.get_remote_address, storage_uri = "redis://localhost:6379", )
cors = CORS()
mail = Mail()
migrate = Migrate()
minio_client = Minio(endpoint = getenv('MINIO_ENDPOINT'),
                     access_key = getenv('MINIO_ACCESS_KEY'),
                     secret_key = getenv('MINIO_SECRET_KEY'),
                     secure = False)