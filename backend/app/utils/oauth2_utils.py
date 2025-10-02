# from app.models.user import Users
# from app.db_utils import db_auth_utils
# from flask_jwt_extended import create_access_token, create_refresh_token
# from datetime import timedelta

# def token_by_GG(user_info):
#     login_email = user_info.get('email').strip()
#     fullname = user_info.get('name').strip()
#     username = fullname.replace(' ','').strip()
#     email = Users.query.filter(Users.email == login_email).first()
#     name = user_info.get('given_name')
#     if not email:
#         db_auth_utils.db_register_gg(username, login_email, name)
#         access_token = create_access_token(identity = username, 
#                                         expires_delta = timedelta(minutes = 15),
#                                         additional_claims = {'role': 'guest'})
#         refresh_token = create_refresh_token(identity = username,
#                                         expires_delta = timedelta(hours = 10),
#                                         additional_claims = {'role': 'guest'})

#     else:
#         role = email.role
#         access_token = create_access_token(identity = username, 
#                                     expires_delta = timedelta(minutes = 15),
#                                     additional_claims = {'role': role})
#         refresh_token = create_refresh_token(identity = username,
#                                     expires_delta = timedelta(hours = 10),
#                                     additional_claims = {'role': role})
        
#     return access_token, refresh_token