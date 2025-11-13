from app.models import Teach_class, Semester, Year, Class_room
from ..base import BaseRepo

from sqlalchemy import select

class AcademicRelationRepo(BaseRepo):    
    def insert_lessons_class(self, data):
        #data: lesson_id, class_room_id, year_id
        self.db.session.add(Teach_class(**data))

    def get_class_room_ids_by_grade_of_lesson_and_year(self, data: dict):
        return self.db.session.scalars(select(Class_room.id).filter(Class_room.grade >= data['lesson_grade'],
                                                           Class_room.year_id == data['year_id'])).all()
                
    def delete_lesson_id_in_teach_class(self, data: dict):
        self.db.session.query(Teach_class).filter(Teach_class.lesson_id == data['lesson_id']).delete(synchronize_session=False)
     
    def set_year_status_to_false(self):
        self.db.session.query(Year).filter(Year.is_active == True).update({Year.is_active: False})

    def set_semester_status_to_false(self):
        self.db.session.query(Semester).filter(Semester.is_active == True).update({Semester.is_active : False})

 


    