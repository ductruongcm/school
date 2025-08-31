from dotenv import load_dotenv
from os import getenv
from urllib.parse import quote

load_dotenv()

class Configs():
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:port/db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lux'