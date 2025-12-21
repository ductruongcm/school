from app.routes import user, student, teacher, oauth2, cloud, auth, export, log, dashboard
from app.routes.academic import core, relation, entity


routes = [oauth2.oauth2_bp, 
          user.user_bp, 
          core.academic_bp,
          student.student_bp,
          teacher.teacher_bp,
          cloud.cloud_bp,
          log.log_bp,
          auth.auth_bp,
          export.export_bp,
          relation.academic_relation_bp,
          entity.academic_entity_bp,
          dashboard.report_bp]
          
