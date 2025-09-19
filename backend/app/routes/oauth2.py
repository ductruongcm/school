from flask import Blueprint, jsonify, request, make_response, redirect
from dotenv import load_dotenv
from os import getenv
import requests
from app.utils import oauth2_utils

from flask_jwt_extended import set_access_cookies, set_refresh_cookies

load_dotenv()

oauth2_bp = Blueprint('oauth2_bp', __name__, url_prefix = '/api/oauth2')

@oauth2_bp.get('/login_gg')
def login_gg():
    # truyền url login của gg để frontend login
    url = ('https://accounts.google.com/o/oauth2/v2/auth?'
           f'client_id={getenv('gg_clientID')}&'
           'redirect_uri=http://localhost:5000/api/oauth2/callback&'
           'response_type=code&'
           'scope=email profile openid')
    return jsonify(url)

@oauth2_bp.get('/callback')
def callback():
    # sau khi nhận được code => đổi lấy token => đổi lấy info
    # từ info, insert to add user => cấp jwt access token
    # đẩy access token vào cookie cùng chuyển hướng cho frontend
    code = request.args.get('code')
    token_res = requests.post("https://oauth2.googleapis.com/token", data = {
        "code": code,
        "client_id": getenv('gg_clientID'),
        "client_secret": getenv('gg_secretkey'),
        'redirect_uri': 'http://localhost:5000/api/oauth2/callback',
        'grant_type': 'authorization_code'
    })
    token = token_res.json()
    GG_access_token = token.get('access_token')
    user_res = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers = {
        "Authorization": f"Bearer {GG_access_token}"
    })
    user_info = user_res.json()
    access_token, refresh_token = oauth2_utils.token_by_GG(user_info)

    response = make_response(redirect('http://localhost:5173/dashboard'))
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response
    