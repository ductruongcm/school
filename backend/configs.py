from dotenv import load_dotenv
from os import getenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

env_file = BASE_DIR/'.env.docker' if getenv('APP_ENV') == 'docker' else BASE_DIR/'.env'
load_dotenv(env_file)

DB_USERNAME = getenv('POSTGRES_USER')
DB_PASSWORD =  getenv('POSTGRES_PASSWORD')
DB_HOST = getenv('POSTGRES_HOST')
DB_PORT = getenv('POSTGRES_PORT')
DB = getenv('POSTGRES_DB')
REDIS_HOST= getenv('REDIS_HOST')
REDIS_PORT = getenv('REDIS_PORT')
jwt_secret_key = getenv('JWT_SECRET_KEY')

if not DB_USERNAME or not DB_PASSWORD:
    raise ValueError('Database username or password not set in environment!')

class Configs:
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    JWT_SECRET_KEY = jwt_secret_key
    JWT_TOKEN_LOCATION = ["cookies"]           #Đọc token từ cookies thay vì header
    JWT_ACCESS_COOKIE_NAME = "access_token"    #Tên cookie chứa access token
    JWT_REFRESH_COOKIE_NAME = "refresh_token"
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_SAMESITE = 'Strict' 
    JWT_COOKIE_CSRF_PROTECT = False          #tắt csrf để test, thực tế phải bật
    JWT_COOKIE_SECURE = False                 #cho phép gửi cookies qua http(ko cần https để test)
    CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"


