from app.routes import user, student, teacher, oauth2, cloud, academic, auth, audit, export

routes = [oauth2.oauth2_bp, 
          user.user_bp, 
          academic.academic_bp,
          student.student_bp,
          teacher.teacher_bp,
          cloud.cloud_bp,
          audit.audit_bp,
          auth.auth_bp,
          export.export_bp]
          
