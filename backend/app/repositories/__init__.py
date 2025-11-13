from .teacher import TeacherRepo
from .log import AuditLogRepo, ActivityLogRepo
from .user import UserRepo
from .academic.core import AcademicAddRepo, AcademicShowRepo, AcademicGetRepo
from .academic.entity import AcademicStudentRepo, AcademicTeacherRepo, ScoreRepo, ScheduleRepo
from .academic.relation import AcademicRelationRepo
from .file import CloudRepo
from .student import StudentsRepo
from .export import ExportRepo

class Repositories:
    def __init__(self, db):
        self.db = db
    
    @property
    def teacher(self):
        return TeacherRepo(self.db)
    
    @property
    def audit_log(self):
        return AuditLogRepo(self.db)
    
    @property
    def activity_log(self):
        return ActivityLogRepo(self.db)
    
    @property 
    def user(self):
        return UserRepo(self.db)
    
    @property
    def academic_get(self):
        return AcademicGetRepo(self.db)
    
    @property
    def academic_show(self):
        return AcademicShowRepo(self.db)
    
    @property
    def academic_add(self):
        return AcademicAddRepo(self.db)
    
    @property
    def academic_student(self):
        return AcademicStudentRepo(self.db)
    
    @property
    def academic_teacher(self):
        return AcademicTeacherRepo(self.db)
    
    @property
    def academic_relation(self):
        return AcademicRelationRepo(self.db)
    
    @property
    def file(self):
        return CloudRepo(self.db)
    
    @property
    def student(self):
        return StudentsRepo(self.db)
    
    @property
    def export(self):
        return ExportRepo(self.db)
    
    @property
    def score(self):
        return ScoreRepo(self.db)

    @property
    def schedule(self):
        return ScheduleRepo(self.db)