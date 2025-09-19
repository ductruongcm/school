from app.routes import user, class_room, student, teacher, oauth2, auth, cloud, monitoring

routes = [oauth2.oauth2_bp, 
          auth.auth_bp, 
          user.user_bp, 
          class_room.class_room_bp,
          student.student_bp,
          teacher.teacher_bp,
          cloud.cloud_bp,
          monitoring.monitoring_bp]
          
