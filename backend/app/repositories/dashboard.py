from app.models import Class_room, Teachers, Score, Score_Type, Student_Period_Summary, Period, Student_Lesson_Period, Attendence, Student_Year_Summary, Grade
from sqlalchemy import func, and_, Numeric, cast, case


class DashboardRepo:
    def __init__(self, db):
        self.db = db

    def show_class_rooms_info_daily(self, data):
        sub = (self.db.session.query(Student_Period_Summary.class_room_id.label('class_room_id'),
                                     func.count(Student_Period_Summary.student_id).label('count_student'),
                                     func.count(Attendence.student_id).filter(Attendence.status == 'E').label('E'),
                                     func.count(Attendence.student_id).filter(Attendence.status == 'A').label('A'))        
                                    .join(Period, Period.id == Student_Period_Summary.period_id)
                                    .outerjoin(Attendence, and_(Attendence.student_id == Student_Period_Summary.student_id,
                                                                Attendence.period_id == Student_Period_Summary.period_id,
                                                                Attendence.date == data.get('day')))
                                    .filter(Period.year_id == data['year_id'],
                                            Period.semester_id == data['semester_id'])
                                    .group_by(Student_Period_Summary.class_room_id,
                                              Period.id)
                                    .subquery())

        return (self.db.session.query(Class_room.id,
                                      Class_room.class_room,
                                      sub.c.count_student,  
                                      sub.c.E,
                                      sub.c.A,
                                      Teachers.name)
                                     .outerjoin(Class_room.teachers)
                                     .outerjoin(sub, Class_room.id == sub.c.class_room_id)
                                     .filter(Class_room.year_id == data['year_id'])
                                     .order_by(Class_room.id)
                                     .all())
    
    def get_academic_student_for_class_by_period(self, data):      
        weighted_score = func.sum(Score.score * Score_Type.weight)
        total_weight = func.sum(Score_Type.weight)
        avg = func.round(cast(weighted_score / total_weight, Numeric), 2)

        sub = (self.db.session.query(Student_Period_Summary.class_room_id.label('class_room_id'),
                                     Student_Lesson_Period.student_id.label('student_id'),
                                     avg.label('avg').label('avg'))
                                            .outerjoin(Student_Lesson_Period, and_(Student_Lesson_Period.student_id == Student_Period_Summary.student_id,
                                                                                   Student_Lesson_Period.period_id == Student_Period_Summary.period_id))
                                            .outerjoin(Student_Lesson_Period.period)
                                            .outerjoin(Student_Lesson_Period.score)
                                            .outerjoin(Score.score_type)
                                            .filter(Period.year_id == data['year_id'],
                                                    Period.semester_id == data['semester_id'])
                                            .group_by(Student_Period_Summary.class_room_id,
                                                      Student_Lesson_Period.student_id,
                                                      Student_Lesson_Period.lesson_id,)
                                            .subquery())
        
        return (self.db.session.query(sub.c.class_room_id,
                                      sub.c.student_id,
                                      func.array_agg(sub.c.avg))
                                      .group_by(sub.c.class_room_id,
                                                sub.c.student_id).all())
    
    def get_summary_by_year_semester(self, data):
        return (self.db.session.query(self.db.session.query(func.count(Class_room.id).filter(Class_room.year_id == data['year_id'])).scalar_subquery(),  
                                         self.db.session.query(func.count(Teachers.id).filter(Teachers.status == True)).scalar_subquery(),  
                                         func.count().filter(Student_Period_Summary.grade == 10),
                                         func.count().filter(Student_Period_Summary.grade == 11),
                                         func.count().filter(Student_Period_Summary.grade == 12),
                                         func.count(Student_Period_Summary.student_id))
                                         .select_from(Student_Period_Summary)
                                         .join(Period, Student_Period_Summary.period_id == Period.id)
                                         .filter(Period.year_id == data['year_id'],
                                                 Period.semester_id == data['semester_id']).one())

    def get_report_of_year_summary_result(self, year_id):
        return (self.db.session.query(func.count(Student_Year_Summary.student_id),
                                      func.count(Student_Year_Summary.status).filter(Student_Year_Summary.status == 'Hoàn thành'),
                                      func.count(Student_Year_Summary.status).filter(Student_Year_Summary.status == 'Lên lớp'),
                                      func.count(Student_Year_Summary.status).filter(Student_Year_Summary.status == 'Lưu ban'),
                                      func.count(Student_Year_Summary.retest_status).filter(Student_Year_Summary.retest_status.isnot(None)),
                                      func.count(Student_Year_Summary.learning_status).filter(Student_Year_Summary.learning_status == 'Tốt'),
                                      func.count(Student_Year_Summary.learning_status).filter(Student_Year_Summary.learning_status == 'Khá'),
                                      func.count(Student_Year_Summary.learning_status).filter(Student_Year_Summary.learning_status == 'Đạt'),
                                      func.count(Student_Year_Summary.is_new_student).filter(Student_Year_Summary.is_new_student.is_(True) & Student_Year_Summary.transfer_info.is_(None)),
                                      func.count(Student_Year_Summary.status).filter(Student_Year_Summary.status == 'Chuyển trường'))
                                      .filter(Student_Year_Summary.year_id == year_id).one())