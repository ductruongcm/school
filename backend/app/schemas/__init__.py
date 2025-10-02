from .auth import Register, Login, SetPassword
from .user import TeacherSchemas, UserSchemas, Student
from .academic import AcademicCreateSchemas, AcademicShowSchemas
from pydantic import ValidationError
from .monitoring import MonitoringShowSchema