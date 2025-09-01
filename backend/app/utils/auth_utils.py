from app.schemas import Users
from app.utils import db_utils
from flask_jwt_extended import create_access_token

def token_by_GG(user_info):
    login_email = user_info.get('email').strip()
    fullname = user_info.get('name').strip()
    username = fullname.replace(' ','').strip()
    email = Users.query.filter(Users.email == login_email).first()
    name = user_info.get('given_name')
    print('thong tin lay dc la',username,name,login_email)
    if not email:
        db_utils.register(username, login_email, name)
        access_token = create_access_token(identity = username, additional_claims = {'role': 'guest'})
    else:
        role = email.role
        access_token = create_access_token(identity = username, additional_claims = {'role': role})
    return access_token