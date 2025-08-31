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
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    JWT_SECRET_KEY = jwt_secret_key