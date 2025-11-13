from app.models import Student_Lesson_Annual, Student_Lesson_Period, Student_Year_Summary, Class_room, Teach_class, Students, Score, Score_Type, Schedule, Lesson, Student_Period_Summary, Period
from sqlalchemy import select, func, and_
from sqlalchemy.dialects.postgresql import insert, aggregate_order_by
from ..base import BaseRepo

class AcademicStudentRepo(BaseRepo):
    #Khu vực cho student
    def insert_student_year_summary(self, data):
        self.db.session.add(Student_Year_Summary(**data))

    def insert_student_period_summary(self, data):
        self.db.session.add(Student_Period_Summary(**data))

    def get_student_year_summary(self, data):
        return self.db.session.query(Student_Year_Summary).filter(Student_Year_Summary.student_id == data['student_id'],
                                                                  Student_Year_Summary.year_id == data['year_id']).scalar()

    def insert_student_lesson_period(self, data):
        self.db.session.add(Student_Lesson_Period(**data))

    def insert_student_lesson_annual(self, data):
        self.db.session.add(Student_Lesson_Annual(**data))

    def get_annual_lesson_totals_by_student_and_year(self, data:dict):   
        return self.db.session.scalars(select(Student_Lesson_Annual.avg_annual).filter(Student_Lesson_Annual.student_id == data['student_id'],
                                                                                       Student_Lesson_Annual.year_id == data['year_id'])).all()
    
    def get_semester_lesson_totals_by_student_and_period(self, data):
        return self.db.session.scalars(select(Student_Lesson_Period.total).filter(Student_Lesson_Period.student_id == data['student_id'],
                                                                                 Student_Lesson_Period.period_id == data['period_id'])).all()
    
    def get_year_lesson_totals_by_student_and_year(self, data):
        return self.db.session.scalars(select(Student_Lesson_Annual.avg_annual).filter(Student_Lesson_Annual.student_id == data['student_id'],
                                                                                       Student_Lesson_Annual.year_id == data['year_id'])).all()

    def get_student_period_summary(self, data):
        return self.db.session.query(Student_Period_Summary).filter(Student_Period_Summary.student_id == data['student_id'],
                                                                    Student_Period_Summary.period_id == data['period_id']).scalar()

    def get_student_lesson_period(self, data):
        return self.db.session.query(Student_Lesson_Period).filter(Student_Lesson_Period.student_id == data['student_id'],
                                                                   Student_Lesson_Period.lesson_id == data['lesson_id'],
                                                                   Student_Lesson_Period.period_id == data['period_id']).scalar()
    
    def show_students_by_class_lesson_period(self, data: dict):
        query = self.db.session.query(Students.id,
                                      Students.name,
                                      Student_Lesson_Period.total,
                                      Student_Lesson_Period.status,
                                      Student_Lesson_Period.note).join(Students.student_lesson_period)\
                                                                 .join(Students.student_year_summary)\
                                                                                       .filter(Student_Year_Summary.class_room_id == data['class_room_id'],                                                                                    
                                                                                               Student_Lesson_Period.period_id == data['period_id'],
                                                                                               Student_Lesson_Period.lesson_id == data['lesson_id'])

        return query.all()
    
    def show_students_for_class_assignment(self, data):
        query = self.db.session.query(Students.id,
                                      Students.student_code,
                                      Students.name,
                                      Student_Year_Summary.score,
                                      Student_Year_Summary.conduct,
                                      Student_Year_Summary.learning_status,
                                      Student_Year_Summary.absent_day,
                                      Class_room.class_room,
                                      Student_Year_Summary.note,
                                      Student_Year_Summary.status,
                                      Student_Year_Summary.grade,
                                      Student_Year_Summary.review_status
                                      ).join(Students.student_year_summary).join(Class_room, Class_room.id == Student_Year_Summary.class_room_id)

        if data['grade']:
            query = query.filter(Student_Year_Summary.grade == data['grade'])

        if data['review_status'] is not None:
            query = query.filter(Student_Year_Summary.review_status == data['review_status'])

        if data['status']:
            query = query.filter(Student_Year_Summary.status == data['status'])

        if data['year_id']:
            query = query.filter(Student_Year_Summary.year_id == data['year_id'])

        return query.filter(Student_Year_Summary.assign_status == False).order_by(Students.student_code).all()
    
    def show_students_for_semester_summary(self, data):
        query = self.db.session.query(Students.id,
                                      Students.name, 
                                      func.jsonb_object_agg(Lesson.lesson, Student_Lesson_Period.total),
                                      Student_Period_Summary.score,
                                      Student_Period_Summary.status,
                                      Student_Period_Summary.conduct,
                                      Student_Period_Summary.absent_day,
                                      Student_Period_Summary.note)\
                                        .join(Students.student_lesson_period)\
                                        .join(Student_Lesson_Period.lesson)\
                                        .join(Student_Lesson_Period.period)\
                                        .join(Student_Period_Summary, and_(Student_Period_Summary.period_id == Student_Lesson_Period.period_id,
                                                                           Student_Period_Summary.student_id == Students.id))
                                        
        if data['year_id']:
            query = query.filter(Period.year_id == data['year_id'])
        
        if data['semester_id']:
            query = query.filter(Period.semester_id == data['semester_id'])

        if data['class_room_id']:
            query = query.filter(Student_Period_Summary.class_room_id == data['class_room_id'])

        return query.group_by(Students.id,
                              Students.name,
                              Student_Period_Summary.score,
                              Student_Period_Summary.conduct,
                              Student_Period_Summary.absent_day,
                              Student_Period_Summary.note,
                              Student_Period_Summary.status).order_by(Students.name).all() 
    
    def show_students_for_year_summary(self, data):
        lessons_subq = (self.db.session.query(Student_Lesson_Annual.student_id.label('id'),
                                              func.jsonb_object_agg(Lesson.lesson,
                                                                    aggregate_order_by(Student_Lesson_Annual.avg_annual, Lesson.id)).label('lessons'))
                                                                    .join(Student_Lesson_Annual.lesson)
                                                                    .join(Student_Year_Summary, Student_Year_Summary.year_id == Student_Lesson_Annual.year_id)
                                                                    .filter(Student_Year_Summary.class_room_id == data['class_room_id'],
                                                                            Student_Lesson_Annual.year_id == data['year_id'])
                                                                    .group_by(Student_Lesson_Annual.student_id).subquery())
        
        absent_subq = (self.db.session.query(Student_Period_Summary.student_id.label('id'),
                                             func.sum(Student_Period_Summary.absent_day).label('absent_sum'))
                                                    .join(Period, Period.id == Student_Period_Summary.period_id)
                                                    .filter(Period.year_id == data['year_id'])
                                                    .group_by(Student_Period_Summary.student_id)
                                                    .subquery())
        
        query = self.db.session.query(Students.id,
                                      Students.name,
                                      lessons_subq.c.lessons,
                                      Student_Year_Summary.score,
                                      Student_Year_Summary.learning_status,
                                      Student_Year_Summary.conduct,
                                      absent_subq.c.absent_sum,
                                      Student_Year_Summary.note).join(Students.student_year_summary)\
                                                                .join(lessons_subq, lessons_subq.c.id == Students.id)\
                                                                .join(absent_subq, absent_subq.c.id == Students.id)\
                                                                            .filter(Student_Year_Summary.year_id == data['year_id'],
                                                                                    Student_Year_Summary.class_room_id == data['class_room_id']).all()
        
        return query

    def get_student_ids_by_period_and_class_room(self, data):
        return self.db.session.scalars(select(Students.id).filter(Student_Period_Summary.class_room_id == data['class_room_id'],
                                                                  Student_Period_Summary.period_id == data['period_id'])).all()
    
    def get_scores_for_year_summary(self, data):
        #year, cls
        subq = (self.db.session.query(Students.id.label('student_id'),
                                      Period.semester_id.label('semester_id'),
                                      func.jsonb_object_agg(Student_Lesson_Period.lesson_id, Student_Lesson_Period.total).label('lessons'))
                                                .join(Students.student_lesson_period)
                                                .join(Student_Lesson_Period.period)
                                                        .filter(Period.year_id == data['year_id'])
                                                        .group_by(Students.id, Period.id).subquery())
        
        query = self.db.session.query(subq.c.student_id,
                                      func.jsonb_object_agg(subq.c.semester_id, subq.c.lessons))\
                                                            .join(Student_Year_Summary, Student_Year_Summary.student_id == subq.c.student_id)\
                                                                    .filter(Student_Year_Summary.class_room_id == data['class_room_id'],
                                                                            Student_Year_Summary.year_id == data['year_id']).group_by(subq.c.student_id).all()

        return query

class AcademicTeacherRepo(BaseRepo):
    #Khu vực cho teacher
    def get_teaching_class_id_by_teacher(self, data: dict):
        return self.db.session.scalars(select(Teach_class.class_room_id).join(Class_room).filter(Class_room.year_id == data['year_id'],
                                                                                          Teach_class.lesson_id == data['lesson_id'],
                                                                                          Teach_class.teacher_id == data['teacher_id'])).all()
    
    def get_teacher_by_lesson_class_year(self, data: dict):    
        #teaching_class_ids, lesson_id, year_id
        return self.db.session.scalars(select(Teach_class.teacher_id).filter(Teach_class.class_room_id.in_(data['teaching_class_ids']), 
                                                                             Teach_class.lesson_id == data['lesson_id'],
                                                                             Teach_class.year_id == data['year_id'])).all()
    
    def get_teaching_class_to_assign_teacher(self, data):
        return self.db.session.query(Teach_class).filter(Teach_class.lesson_id == data['lesson_id'],
                                                         Teach_class.year_id == data['year_id'],
                                                         Teach_class.class_room_id.in_(data['teaching_class_ids'])).all()
    
    def get_teaching_class_to_remove_teacher(self, data):
        return self.db.session.query(Teach_class).filter(Teach_class.year_id == data['year_id'],
                                                         Teach_class.teacher_id == data['teacher_id'],
                                                         Teach_class.class_room_id.in_(data['teaching_class_ids']))
    
    def get_teaching_class_by_teacher_year(self, data: dict):
        return self.db.session.query(Teach_class).filter(Teach_class.year_id == data['year_id'],
                                                         Teach_class.teacher_id == data['teacher_id']).all()
    
    def get_home_class_by_teacher_and_year(self, data: dict):
        return self.db.session.query(Class_room).filter(Class_room.teacher_id == data['teacher_id'],
                                                        Class_room.year_id == data['year_id']).first()
    
class ScoreRepo(BaseRepo):
    def show_scores_by_class_room(self, data: dict):
        query = self.db.session.query(Students.id,
                                      Students.name,
                                      Student_Lesson_Period.note).join(Students.student_lesson_period)\
                                                                 .join(Students.student_year_summary)\
                                                                                       .filter(Student_Year_Summary.class_room_id == data['class_room_id'],                                                                                    
                                                                                               Student_Lesson_Period.period_id == data['period_id'],
                                                                                               Student_Lesson_Period.lesson_id == data['lesson_id'])

        return query.all()
    
    def get_score(self, student_id, period_id, lesson_id, attempt, type_score_id):
        return self.db.session.query(Score.score).filter(Score.attempt == attempt,
                                                         Score.score_type_id == type_score_id,
                                                         Student_Lesson_Period.student_id == student_id,
                                                         Student_Lesson_Period.lesson_id == lesson_id,
                                                         Student_Lesson_Period.period_id == period_id).join(Score.student_lesson_period).scalar()

    def init_score_frame(self):
        return self.db.session.query(Score_Type.id, Score_Type.max_count).all()

    def get_score_type_ids(self):
        return self.db.session.scalars(select(Score_Type.id)).all()
    
    def upsert_score(self, data):
        stmt = insert(Score).values(**data)
        stmt = stmt.on_conflict_do_update(index_elements = [Score.student_lesson_period_id, Score.score_type_id, Score.attempt],
                                          set_ = {'score': stmt.excluded.score},
                                          where = stmt.excluded.score != Score.score)
        
        self.db.session.execute(stmt)
    
    def get_scores_by_student_lesson_period_id(self, data):
        query = self.db.session.query(Score_Type.weight, 
                                      func.array_agg(Score.score)).join(Score.score_type).filter(Score.student_lesson_period_id == data).group_by(Score_Type.weight)
        
        return query.order_by(Score_Type.weight.asc()).all()
    
class ScheduleRepo(BaseRepo):
    def bulk_upsert_schedule(self, data: dict):
        stmt = insert(Schedule).values(**data)
        stmt = stmt.on_conflict_do_update(index_elements = [Schedule.class_room_id, 
                                                            Schedule.period_id, 
                                                            Schedule.day_of_week, 
                                                            Schedule.lesson_time], 
                                          set_ = {'lesson_id': stmt.excluded.lesson_id},
                                          where = stmt.excluded.lesson_id != Schedule.lesson_id)
        self.db.session.execute(stmt)

    def delete_schedule(self, data: dict):
        self.db.session.query(Schedule).filter(Schedule.class_room_id == data['class_room_id'],
                                               Schedule.period_id == data['period_id'],
                                               Schedule.day_of_week == data['day_of_week'],
                                               Schedule.lesson_time == data['lesson_time']).delete(synchronize_session = False)
        
            
    def show_lesson_for_schedules(self, period_id, class_room_id, day_of_week, lesson_time):
        return self.db.session.query(Lesson.id, Lesson.lesson)\
                                                        .join(Schedule.lesson)\
                                                                    .filter(Schedule.period_id == period_id,
                                                                            Schedule.class_room_id == class_room_id,
                                                                            Schedule.day_of_week == day_of_week,
                                                                            Schedule.lesson_time == lesson_time).all()
        
