from .auth import Login, SetPassword, Username, Password, Tmp_token, Role
from .user import TeacherSchemas, UserSchemas, StudentSchemas
from .academic import AcademicShowSchemas, AcademicSchemas, AcademicUpdateSchemas
from pydantic import ValidationError
from .audit import AuditShowSchema, ActivityShowSchema
from .file import CloudSchemas