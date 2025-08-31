from flask import Blueprint, jsonify, request
from dotenv import load_dotenv
from os import getenv
import requests

load_dotenv()

oauth2_bp = Blueprint('oauth2_bp', __name__, url_prefix = '/api/oauth2')

@oauth2_bp.get('/login_gg')
def login_gg():
    # truyền url login của gg để frontend login
    url = ('https://accounts.google.com/o/oauth2/v2/auth?'
           f'client_id={getenv('gg_clientID')}&'
           f'redirect_uri={getenv('gg_redirect_uri')}I&'
           'response_type=code&'
           'scope=email profile openid')
    return jsonify(url)

@oauth2_bp.get('/callback')
def callback():
    # sau khi nhận được code => đổi lấy token => đổi lấy info
    code = request.args.get('code')
    token_res = requests.post("https://oauth2.googleapis.com/token", data = {
        "code": code,
        "client_id": getenv('gg_clientID'),
        "client_secret": getenv('gg_secretkey'),
        'redirect_uri': getenv('gg_redirect_uri'),
        'grant_type': 'authorization_code'
    })
    token = token_res.json()
    access_token = token.get('access_token')
    user_res = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers = {
        "Authorization": f"Bearer {access_token}"
    })
    user_info = user_res.json()
    print(user_info)