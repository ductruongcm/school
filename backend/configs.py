from dotenv import load_dotenv
from os import getenv
from urllib.parse import quote_plus

load_dotenv()

db_username = quote_plus(getenv('db_username'))
db_password = quote_plus(getenv('db_password'))
jwt_secret_key = quote_plus(getenv('jwt_secret_key'))


class Configs():
    SQLALCHEMY_DATABASE_URI = f'postgresql://{db_username}:{db_password}@localhost:5432/school'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    JWT_SECRET_KEY = jwt_secret_key
    JWT_TOKEN_LOCATION = ['cookies']            #Đọc token từ cookies thay vì header
    JWT_ACCESS_COOKIE_NAME = 'access_token'     #Tên cookie chứa access token
    JWT_REFRESH_COOKIE_NAME = 'refresh_token'
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_CSRF_PROTECTION = True           #tắt csrf để test, thực tế phải bật
    JWT_COOKIE_SECURE = False                   #cho phép gửi cookies qua http(ko cần https để test)
