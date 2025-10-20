from .auth import Register, Login, SetPassword, Username, Password
from .user import TeacherSchemas, UserSchemas, StudentSchemas
from .academic import AcademicShowSchemas, AcademicSchemas
from pydantic import ValidationError
from .audit import AuditShowSchema
from .file import CloudSchemas