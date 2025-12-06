from app.models import Class_room, Teachers, Score, Score_Type, Student_Period_Summary, Period, Student_Lesson_Period
from sqlalchemy import func, and_, Numeric, cast, Integer, true
from datetime import date

class DashboardRepo:
    def __init__(self, db):
        self.db = db

    def show_class_rooms_info_by_year(self, data):
        sub = (self.db.session.query(Student_Period_Summary.class_room_id.label('class_room_id'),
                                     func.count(Student_Period_Summary.student_id).label('student_count'))
                                     .join(Period, Student_Period_Summary.period_id == Period.id)
                                     .filter(Period.year_id == data['year_id'],
                                             Period.semester_id == data['semester_id'])
                                     .group_by(Student_Period_Summary.class_room_id)
                                     .subquery())
        
        return (self.db.session.query(Class_room.id,
                                      Class_room.class_room,
                                      cast(sub.c.student_count, Integer),
                                      Teachers.name)
                                        .outerjoin(Class_room.teachers)
                                        .outerjoin(sub, sub.c.class_room_id == Class_room.id)
                                        .filter(Class_room.year_id == data['year_id'])
                                        .order_by(Class_room.id).all())
                                             
    def get_academic_student_for_class_by_period(self, data):      
        weighted_score = func.sum(Score.score * Score_Type.weight)
        total_weight = func.sum(Score_Type.weight)
        avg = func.round(cast(weighted_score / total_weight, Numeric), 2)

        return (self.db.session.query(Student_Period_Summary.class_room_id,
                                      Student_Lesson_Period.student_id,
                                      avg)
                                      .join(Student_Lesson_Period, and_(Student_Lesson_Period.student_id == Student_Period_Summary.student_id,
                                                                        Student_Lesson_Period.period_id == Student_Period_Summary.period_id))
                                      .join(Student_Lesson_Period.period)
                                      .join(Student_Lesson_Period.score)
                                      .join(Score.score_type)
                                      .filter(Period.year_id == data['year_id'],
                                              Period.semester_id == data['semester_id'])
                                      .group_by(Student_Period_Summary.class_room_id,
                                                Student_Lesson_Period.lesson_id,
                                                Student_Lesson_Period.student_id)
                                      .all())
    
    def get_summary_by_year_semester(self, data):
        summary = (self.db.session.query(self.db.session.query(func.count(Class_room.id).filter(Class_room.year_id == data['year_id'])).scalar_subquery(),  
                                         self.db.session.query(func.count(Teachers.id).filter(Teachers.status == True)).scalar_subquery(),  
                                         func.count().filter(Student_Period_Summary.grade == 10),
                                         func.count().filter(Student_Period_Summary.grade == 11),
                                         func.count().filter(Student_Period_Summary.grade == 12),
                                         func.count(Student_Period_Summary.student_id))
                                         .select_from(Student_Period_Summary)
                                         .join(Period, Student_Period_Summary.period_id == Period.id)
                                         .filter(Period.year_id == data['year_id'],
                                                 Period.semester_id == data['semester_id']).one())
        return summary