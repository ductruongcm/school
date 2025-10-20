from .base import BaseRepo
from app.models import Students, Student_info, Users, Class_room

class Export_Repo(BaseRepo):
   def user_list(self, data: dict):
        fields = self.filter_context('class_room_id', 'year_id', context=data)
        return self.db.session.query(Students.name,
                                     Students.student_code,
                                     Student_info.gender,
                                     Student_info.BOD,
                                     Users.username,
                                     Users.tmp_password,
                                     Class_room.class_room).join(Students.student_info)\
                                                           .join(Students.users)\
                                                           .join(Students.class_room).filter(Class_room.id == fields['class_room_id'],
                                                                                             Class_room.year_id == fields['year_id']).all()