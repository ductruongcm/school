from app.routes import user, class_room, student, teacher
from app.routes.oauth2 import oauth2
from app.routes.auth import auth



routes = [oauth2.oauth2_bp, 
          auth.auth_bp, 
          user.user_bp, 
          class_room.class_room_bp,
          student.student_bp,
          teacher.teacher_bp]
          
