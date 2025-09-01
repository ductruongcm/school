from app.routes import oauth2, auth

routes = [oauth2.oauth2_bp, auth.auth_bp]