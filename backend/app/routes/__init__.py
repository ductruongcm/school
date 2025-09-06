from app.routes.user import user
from app.routes.auth import auth
from app.routes.oauth2 import oauth2
from app.routes.class_room import class_room

routes = [oauth2.oauth2_bp, auth.auth_bp, user.user_bp, class_room.class_room_bp]
