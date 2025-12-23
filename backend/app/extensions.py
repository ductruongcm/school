from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter, util
from flask_cors import CORS
from flask_migrate import Migrate
from minio import Minio
from pathlib import Path
from os import getenv
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env_file = BASE_DIR/'.env.docker' if getenv('APP_ENV') == 'docker' else BASE_DIR/'.env'
load_dotenv(env_file)

REDIS_HOST = getenv('REDIS_HOST')
REDIS_PORT = getenv('REDIS_PORT')
BUCKET_NAME = getenv('BUCKET_NAME')

db = SQLAlchemy()
jwt = JWTManager()
lm = Limiter(key_func = util.get_remote_address, storage_uri = f"redis://{REDIS_HOST}:{REDIS_PORT}/1" )
cors = CORS()
migrate = Migrate()
minio_client = Minio(endpoint = getenv('MINIO_ENDPOINT', 'localhost:9000'),
                     access_key = getenv('MINIO_ROOT_USER'),
                     secret_key = getenv('MINIO_ROOT_PASSWORD'),
                     secure = False)