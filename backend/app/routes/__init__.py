from app.routes import user, student, teacher, oauth2, cloud, monitoring, academic

routes = [oauth2.oauth2_bp, 
          user.user_bp, 
          academic.academic_bp,
          student.student_bp,
          teacher.teacher_bp,
          cloud.cloud_bp,
          monitoring.monitoring_bp]
          
