from app.models import Student_Lesson_Annual, Student_Lesson_Period, Student_Year_Summary, Class_room, \
                       Teach_class, Students, Score, Score_Type, Student_Period_Summary, Retest,\
                       Period, Users, Teachers, Lesson, Schedule, LessonTag, Attendence, Semester
from sqlalchemy import select, func, and_, cast, String, Numeric, case, or_, literal, update
from sqlalchemy.orm import aliased
from sqlalchemy.dialects.postgresql import insert
from ..base import BaseRepo
from datetime import date

class AcademicStudentRepo(BaseRepo):
    #Khu vực cho student
    def insert_student_year_summary(self, data):
        self.db.session.add(Student_Year_Summary(**data))

    def insert_student_period_summary(self, data):
        self.db.session.add(Student_Period_Summary(**data))

    def insert_student_period_summary_for_new_year(self, data):
        stmt = (insert(Student_Period_Summary)
                    .from_select([Student_Period_Summary.student_id,
                                  Student_Period_Summary.class_room_id,
                                  Student_Period_Summary.grade,
                                  Student_Period_Summary.period_id], select(literal(data['student_id']),
                                                                            literal(data['class_room_id']),
                                                                            literal(data['grade']),
                                                                            Period.id).where(Period.year_id == data['year_id'])))
        stmt = stmt.on_conflict_do_nothing(constraint='stu_per_uniq')
        self.db.session.execute(stmt)

    def insert_student_lesson_period_for_new_year(self, data):
        sub_lesson = select(Lesson.id.label('lesson_id')).join(Lesson.lessontag).where(Lesson.grade <= data['grade'], LessonTag.is_visible.is_(True)).subquery()
        
        stmt = (insert(Student_Lesson_Period).from_select([Student_Lesson_Period.student_id,
                                                           Student_Lesson_Period.lesson_id,
                                                           Student_Lesson_Period.period_id],
                                                           select(literal(data['student_id']),
                                                                  sub_lesson.c.lesson_id,
                                                                  Period.id).where(Period.year_id == data['year_id'])))
        
        stmt = stmt.on_conflict_do_nothing(constraint='stu_ls_per_uniq')
        self.db.session.execute(stmt)

    def get_student_year_summary(self, data):
        return self.db.session.query(Student_Year_Summary).filter(Student_Year_Summary.student_id == data['student_id'],
                                                                  Student_Year_Summary.year_id == data['year_id']).scalar()
    
    def get_student_lesson_annual(self, data):
        return self.db.session.query(Student_Lesson_Annual).filter(Student_Lesson_Annual.student_id == data['student_id'],
                                                                   Student_Lesson_Annual.lesson_id == data['lesson_id'],
                                                                   Student_Lesson_Annual.year_id == data['year_id']).scalar()

    def upsert_student_lesson_period(self, data):
        stmt = insert(Student_Lesson_Period).values(data)

        stmt = stmt.on_conflict_do_update(index_elements=['student_id', 'period_id', 'lesson_id'],
                                          set_={Student_Lesson_Period.total: stmt.excluded.total,
                                                Student_Lesson_Period.status: stmt.excluded.status},
                                          where=or_(stmt.excluded.total.is_distinct_from(Student_Lesson_Period.total),
                                                    stmt.excluded.status.is_distinct_from(Student_Lesson_Period.status)))
        self.db.session.execute(stmt)

    def upsert_student_lesson_annual(self, data):
        stmt = insert(Student_Lesson_Annual).values(data)
        stmt = stmt.on_conflict_do_update(index_elements=['student_id', 'lesson_id', 'year_id'],
                                          set_=({Student_Lesson_Annual.avg_annual: stmt.excluded.avg_annual,
                                                 Student_Lesson_Annual.status: stmt.excluded.status}),
                                          where=or_(stmt.excluded.avg_annual.is_distinct_from(Student_Lesson_Annual.avg_annual),
                                                    stmt.excluded.status.is_distinct_from(Student_Lesson_Annual.status)))

        self.db.session.execute(stmt)
    
    def get_semester_lesson_totals_by_student_and_period(self, data):
        return (self.db.session.query(Student_Lesson_Period.period_id,
                                      func.array_agg(Student_Lesson_Period.total))
                                      .join(Student_Lesson_Period.period)
                                      .filter(Student_Lesson_Period.student_id == data['student_id'],
                                              Period.year_id == data['year_id'])
                                      .group_by(Student_Lesson_Period.period_id).all())
    
    def get_annual_lesson_totals_by_student_and_year(self, data):
        return (self.db.session.scalars(select(Student_Lesson_Annual.avg_annual)
                                        .filter(Student_Lesson_Annual.year_id == data['year_id'],
                                                Student_Lesson_Annual.student_id == data['student_id'])).all())

    def get_student_period_summary(self, data):
        return self.db.session.query(Student_Period_Summary).filter(Student_Period_Summary.student_id == data['student_id'],
                                                                    Student_Period_Summary.period_id == data['period_id']).scalar()

    def get_student_lesson_period(self, data):
        return self.db.session.query(Student_Lesson_Period).filter(Student_Lesson_Period.student_id == data['student_id'],
                                                                   Student_Lesson_Period.lesson_id == data['lesson_id'],
                                                                   Student_Lesson_Period.period_id == data['period_id']).scalar()
    
    def get_class_room_by_student_period(self, data):
        return (self.db.session.query(Class_room.id, Class_room.class_room)
                                .join(Class_room, Student_Period_Summary.class_room_id == Class_room.id,
                                      Period, Student_Period_Summary.period_id == Period.id)
                                      .filter(Period.year_id == data['year_id'],
                                              Period.semester_id == data['semester_id'],
                                              Student_Period_Summary.student_id == data['student_id'])
                                              .all())
    
    def show_students_by_class_lesson_period(self, data: dict):
        return (self.db.session.query(Students.id,
                                      Students.name,
                                      Student_Lesson_Period.total,
                                      Student_Lesson_Period.status,
                                      Student_Lesson_Period.note)
                                            .join(Students.student_lesson_period)
                                            .join(Student_Lesson_Period.period)
                                            .join(Student_Period_Summary, and_(Student_Period_Summary.period_id == Period.id,
                                                                               Student_Period_Summary.student_id == Students.id))
                                                    .filter(Student_Period_Summary.class_room_id == data['class_room_id'],                                                                                    
                                                            Period.year_id == data['year_id'],
                                                            Period.semester_id == data['semester_id'],
                                                            Student_Lesson_Period.lesson_id == data['lesson_id']).all())
    
    def show_students_for_class_assignment(self, data):
        subq = (self.db.session.query(Student_Year_Summary.student_id.label('student_id'),
                                     Student_Year_Summary.score.label('score'),
                                     Student_Year_Summary.conduct.label('conduct'),
                                     Student_Year_Summary.learning_status.label('learning_status'),
                                     Class_room.class_room.label('class_room'),
                                     Student_Year_Summary.note.label('note'),
                                     Student_Year_Summary.status.label('status'))
                                     .outerjoin(Class_room, Class_room.id == Student_Year_Summary.class_room_id)
                                     .filter(Student_Year_Summary.year_id == data['prev_year_id'],
                                             Student_Year_Summary.assign_status == data['assign_status']).subquery())
        
        query = self.db.session.query(Students.id,
                                      Students.student_code,
                                      Students.name,
                                      subq.c.score,
                                      subq.c.conduct,
                                      subq.c.learning_status,
                                      subq.c.class_room,
                                      subq.c.note,
                                      subq.c.status,
                                      Class_room.class_room,
                                      Student_Year_Summary.class_room_id)\
                                            .join(Students.student_year_summary)\
                                            .join(subq, subq.c.student_id == Students.id)\
                                            .outerjoin(Class_room, Class_room.id == Student_Year_Summary.class_room_id)\
                                                .filter(Student_Year_Summary.year_id == data['year_id'],
                                                        Student_Year_Summary.grade == data['grade'])

        return query.order_by(Students.student_code).all()
    
    def show_students_for_approval(self, data):
        query = (self.db.session.query(Students.id,
                                      Students.student_code,
                                      Students.name,
                                      Student_Year_Summary.score,
                                      Student_Year_Summary.conduct,
                                      Student_Year_Summary.learning_status,
                                      Student_Year_Summary.absent_day,
                                      Class_room.class_room,
                                      Student_Year_Summary.note,
                                      Student_Year_Summary.status,
                                      Student_Year_Summary.review_status)
                                            .join(Students.student_year_summary)
                                            .outerjoin(Class_room, and_(Class_room.id == Student_Year_Summary.class_room_id,
                                                                        Class_room.year_id == Student_Year_Summary.year_id))
                                                    .filter(Student_Year_Summary.grade == data['grade'],
                                                            Student_Year_Summary.year_id == data['year_id'],
                                                            Student_Year_Summary.review_status.isnot(True),
                                                            Student_Year_Summary.is_new_student.is_(True)))

        if data['status']:
            query = query.filter(Student_Year_Summary.status.ilike(f"%{data['status']}%"))

        return query.all()
        
    
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

    def upsert_student_year_summary(self, data):
        stmt = insert(Student_Year_Summary).values(data)
        stmt = stmt.on_conflict_do_update(index_elements = [Student_Year_Summary.student_id, Student_Year_Summary.year_id],
                                          set_ = {'grade': stmt.excluded.grade},
                                          where = stmt.excluded.grade.is_distinct_from(Student_Year_Summary.grade))        
        self.db.session.execute(stmt)

    def show_class_room_by_student_period(self, data):
        return (self.db.session.query(Class_room.id, Class_room.class_room, Class_room.grade)
                .join(Users.students)
                .join(Students.student_period_summary)
                .join(Class_room, Student_Period_Summary.class_room_id == Class_room.id)
                .join(Period, Period.id == Student_Period_Summary.period_id)
                        .filter(Period.year_id == data['year_id'],
                                Period.semester_id == data['semester_id'],
                                Users.id == data['user_id']).all())
    
    #student_lesson_frame cho tong ket nam hoc va hoc ky
    def get_lessons_and_students_for_summary(self, data):
        return (self.db.session.query(Student_Year_Summary.student_id,
                                      cast(Lesson.id, String), Lesson.lesson)
                                      .join(Student_Year_Summary, Student_Year_Summary.grade >= Lesson.grade)
                                      .join(Lesson.lessontag)
                                      .filter(Lesson.grade <= data['grade'],
                                              LessonTag.is_visible == True,
                                              Student_Year_Summary.class_room_id== data['class_room_id']).all())
    
    ### Tong ket mon hoc hoc ky
    def get_semester_lesson_total_by_student_for_class(self, data):
        sub = (self.db.session.query(Student_Lesson_Period.student_id.label('student_id'),
                                     Student_Lesson_Period.lesson_id.label('lesson_id'),
                                     Lesson.lesson.label('lesson'),
                                     Student_Lesson_Period.total.label('total'),
                                     Period.id.label('period_id'))
                               .join(Student_Lesson_Period.lesson)
                               .join(Student_Lesson_Period.period)
                               .filter(Period.semester_id == data['semester_id'],
                                        Period.year_id == data['year_id'])
                               .subquery())
 
        return (self.db.session.query(sub.c.student_id,
                                      func.jsonb_object_agg(sub.c.lesson_id,
                                                            func.jsonb_build_object(sub.c.lesson, sub.c.total)))
                               .join(Student_Period_Summary, and_(Student_Period_Summary.student_id == sub.c.student_id,
                                                                  Student_Period_Summary.period_id == sub.c.period_id))
                               .filter(Student_Period_Summary.class_room_id == data.get('class_room_id'))
                               .order_by(sub.c.student_id)
                               .group_by(sub.c.student_id)
                               .all())
    
    def get_temp_student_semester_summary_infos(self, data):
        sub_absent_day = (self.db.session.query(Attendence.student_id.label('student_id'),
                                                func.sum(case((Attendence.status != 'P', 1), else_= 0)).label('count_absent_day'))
                                         .join(Attendence.period)
                                         .join(Student_Period_Summary, and_(Student_Period_Summary.student_id == Attendence.student_id,
                                                                            Student_Period_Summary.period_id == Period.id))
                                         .filter(Period.year_id == data['year_id'],
                                                 Period.semester_id == data['semester_id'],
                                                 Student_Period_Summary.class_room_id == data['class_room_id']
                                                 )
                                         .group_by(Attendence.student_id).subquery())
        
        sub_score = (self.db.session.query(Student_Lesson_Period.student_id.label('student_id'),
                                           case(((func.count(Student_Lesson_Period.student_id) == func.count(Student_Lesson_Period.total)), 
                                                  func.round(cast(func.avg(Student_Lesson_Period.total), Numeric), 2)), else_=None).label('total'))
                                    .join(Student_Lesson_Period.period)
                                    .join(Student_Period_Summary, and_(Student_Period_Summary.student_id == Student_Lesson_Period.student_id,
                                                                       Student_Period_Summary.period_id == Student_Lesson_Period.period_id))
                                    .filter(Period.year_id == data['year_id'],
                                            Period.semester_id == data['semester_id'],
                                            Student_Period_Summary.class_room_id == data['class_room_id'])
                                    .group_by(Student_Lesson_Period.student_id)
                                    .subquery())
    
        return (self.db.session.query(Student_Period_Summary.student_id,
                                      Students.name,
                                      sub_score.c.total,
                                      Student_Period_Summary.status,
                                      Student_Period_Summary.conduct,
                                      sub_absent_day.c.count_absent_day,
                                      Student_Period_Summary.note)
                            .join(Student_Period_Summary.students)
                            .outerjoin(sub_score, sub_score.c.student_id == Student_Period_Summary.student_id)
                            .outerjoin(sub_absent_day, sub_absent_day.c.student_id == Student_Period_Summary.student_id)
                            .join(Period, Period.id == Student_Period_Summary.period_id)
                            .filter(Period.year_id == data['year_id'],
                                    Period.semester_id == data['semester_id'],
                                    Student_Period_Summary.class_room_id == data['class_room_id'])
                            .order_by(Student_Period_Summary.student_id)
                            .all())
    
    def get_student_semester_summary_infos(self, data):       
        return (self.db.session.query(Student_Period_Summary.student_id,
                                      Students.name,
                                      Student_Period_Summary.score,
                                      Student_Period_Summary.status,
                                      Student_Period_Summary.conduct,
                                      Student_Period_Summary.absent_day,
                                      Student_Period_Summary.note)
                                      .join(Student_Period_Summary.students)
                                      .join(Period, Student_Period_Summary.period_id == Period.id)
                                      .filter(Student_Period_Summary.class_room_id == data.get('class_room_id'),
                                              Period.year_id == data['year_id'],
                                              Period.semester_id == data['semester_id'])
                                      .order_by(Student_Period_Summary.student_id)
                                      .all())
    
    def calc_lesson_total_by_class_year_for_student(self, data):
        weighted_period_total = func.sum(Student_Lesson_Period.total * Semester.weight)
        total_weight = func.sum(Semester.weight)
        count_total = func.count(Student_Lesson_Period.total)
        count_weight = func.count(Semester.weight)
        avg = case((count_total == count_weight, func.round(cast(weighted_period_total / total_weight, Numeric), 2)), else_=None)
        status = case((avg >= 5, True), else_= False)
        return (self.db.session.scalars(select(func.jsonb_build_object(
                                                    'student_id', Student_Year_Summary.student_id,
                                                    'lesson_id', Student_Lesson_Period.lesson_id, 
                                                    'avg_annual', avg.label('avg'),
                                                    'year_id', Student_Year_Summary.year_id,
                                                    'status', status))
                                .join(Student_Lesson_Period, Student_Lesson_Period.student_id == Student_Year_Summary.student_id)
                                .join(Student_Lesson_Period.period)
                                .join(Semester, Semester.id == Period.semester_id)
                                .filter(Student_Year_Summary.class_room_id == data['class_room_id'],
                                        Period.year_id == data['year_id'])
                                .group_by(Student_Year_Summary.student_id, Student_Lesson_Period.lesson_id, Student_Year_Summary.year_id))
                                .all())

    def get_avg_for_student_lesson_period(self, data):
        return (self.db.session.query(Student_Period_Summary.student_id,
                                      func.array_agg(Student_Lesson_Period.total),
                                      func.round(cast(func.avg(Student_Lesson_Period.total), Numeric), 2))
                                      .join(Student_Lesson_Period, and_(Student_Lesson_Period.student_id == Student_Period_Summary.student_id,
                                                                        Student_Lesson_Period.period_id == Student_Period_Summary.period_id))
                                      .join(Period, Student_Period_Summary.period_id == Period.id)
                                      .filter(Student_Period_Summary.class_room_id == data['class_room_id'],
                                              Period.year_id == data['year_id'],
                                              Period.semester_id == data['semester_id'])
                                      .group_by(Student_Period_Summary.student_id,
                                                Student_Lesson_Period.student_id)  
                                      .all())
    
    ### Tong ket nam hoc
    def get_year_lesson_total_by_student_for_class(self, data):
        return (self.db.session.query(Student_Year_Summary.student_id,
                                      func.jsonb_object_agg(Lesson.id,
                                                            func.jsonb_build_object(Lesson.lesson, Student_Lesson_Annual.avg_annual)))
                               .join(Lesson, Student_Year_Summary.grade >= Lesson.grade)
                               .join(Lesson.lessontag) 
                               .outerjoin(Student_Lesson_Annual, and_(Student_Year_Summary.student_id == Student_Lesson_Annual.student_id,
                                                                      Student_Year_Summary.year_id == Student_Lesson_Annual.year_id,
                                                                      Student_Lesson_Annual.lesson_id == Lesson.id))       
                               .filter(Student_Year_Summary.year_id == data['year_id'],
                                       Student_Year_Summary.class_room_id == data['class_room_id'],
                                       LessonTag.is_visible == True)
                               .group_by(Student_Year_Summary.student_id) 
                               .all())
    
    def get_temp_year_lesson_total_by_student_for_class(self, data):
        weighted_total = func.sum(Student_Lesson_Period.total * Semester.weight)
        sum_weight = func.sum(Semester.weight)
        avg_annual = func.round(cast(weighted_total / sum_weight, Numeric), 2)
        sub = (self.db.session.query(Student_Year_Summary.student_id.label('student_id'),
                                     Student_Lesson_Period.lesson_id.label('lesson_id'),
                                     Lesson.lesson.label('lesson'),
                                     avg_annual.label('avg_annual'))
                              .join(Student_Lesson_Period, Student_Lesson_Period.student_id == Student_Year_Summary.student_id)
                              .join(Student_Lesson_Period.lesson)
                              .join(Period, and_(Student_Year_Summary.year_id == Period.year_id,
                                                 Period.id == Student_Lesson_Period.period_id))
                              .join(Semester, Semester.id == Period.semester_id)
                              .filter(Student_Year_Summary.class_room_id == data['class_room_id'],
                                      Period.year_id == data['year_id'])
                              .group_by(Student_Year_Summary.student_id,
                                        Student_Lesson_Period.lesson_id,
                                        Lesson.lesson).subquery())
     
        return (self.db.session.query(sub.c.student_id,
                                      func.jsonb_object_agg(sub.c.lesson_id, func.jsonb_build_object(sub.c.lesson, sub.c.avg_annual)))
                                            .group_by(sub.c.student_id)      
                                            .all())
    
    def get_avg_annual_by_class_year(self, data):
        return (self.db.session.query(Student_Year_Summary.student_id,
                                      func.array_agg(Student_Lesson_Annual.avg_annual))
                                      .join(Student_Lesson_Annual, and_(Student_Year_Summary.student_id == Student_Lesson_Annual.student_id,
                                                                        Student_Year_Summary.year_id == Student_Lesson_Annual.year_id))
                                      .filter(Student_Year_Summary.class_room_id == data['class_room_id'],
                                              Student_Year_Summary.year_id == data['year_id'])
                                      .group_by(Student_Year_Summary.student_id)
                                      .all())
    
    def get_student_year_summary_infos(self, data):
        sub_absent_day = (self.db.session.query(Attendence.student_id.label('student_id'),
                                                func.count(Attendence.status).filter(Attendence.status != 'P').label('count'))
                                                .join(Attendence.period)
                                                .filter(Period.year_id == data['year_id'])
                                                .group_by(Attendence.student_id)
                                                .subquery())
        
        return (self.db.session.query(Student_Year_Summary.student_id,
                                      Students.name,
                                      Student_Year_Summary.score,
                                      Student_Year_Summary.learning_status,
                                      Student_Year_Summary.conduct,
                                      sub_absent_day.c.count,
                                      Student_Year_Summary.note)
                                      .join(Student_Year_Summary.students)
                                      .outerjoin(sub_absent_day, sub_absent_day.c.student_id == Student_Year_Summary.student_id)
                                      .filter(Student_Year_Summary.year_id == data['year_id'],
                                              Student_Year_Summary.class_room_id == data['class_room_id'])
                                      .order_by(Student_Year_Summary.student_id)
                                      .all())

    def get_weak_students(self, data):
        subq_filter = (self.db.session.query(Student_Lesson_Period.student_id.label('student_id'),
                                             Student_Period_Summary.class_room_id.label('class_room_id'),
                                             Student_Period_Summary.grade.label('grade'),
                                             Period.id.label('period_id'))
                                            .join(Period, and_(Student_Lesson_Period.period_id == Period.id,
                                                               Period.year_id == data['year_id'],
                                                               Period.semester_id == data['semester_id']))
                                            .join(Student_Period_Summary, and_(Student_Period_Summary.student_id == Student_Lesson_Period.student_id,
                                                                               Student_Period_Summary.period_id == Period.id))
                                            .join(Student_Lesson_Period.score)
                                            .join(Score.score_type)
                                            .group_by(Student_Lesson_Period.student_id, Student_Period_Summary.class_room_id, Student_Period_Summary.grade, Period.id, Student_Lesson_Period.lesson_id)
                                            .having(func.sum(Score.score * Score_Type.weight) / func.sum(Score_Type.weight) < 5)
                                            .distinct())
        
        if data.get('grade'):
            subq_filter = subq_filter.filter(Student_Period_Summary.grade == data['grade'])
        
        if data.get('class_room_id'):
            subq_filter = subq_filter.filter(Student_Period_Summary.class_room_id == data['class_room_id'])

        subq_filter = subq_filter.subquery()

        subq = (self.db.session.query(Class_room.class_room.label('class_room'),
                                      Students.name.label('name'),
                                      Lesson.id.label('lesson_id'),
                                      Lesson.lesson.label('lesson'),
                                      func.round(cast(func.sum(Score.score * Score_Type.weight) / func.sum(Score_Type.weight), Numeric), 2).label('avg'))
                                      .join(LessonTag, and_(Lesson.id == LessonTag.lesson_id,
                                                            LessonTag.is_visible == True))
                                      .outerjoin(subq_filter, subq_filter.c.grade >= Lesson.grade)
                                      .outerjoin(Students, subq_filter.c.student_id == Students.id)
                                      .outerjoin(Class_room, Class_room.id == subq_filter.c.class_room_id)
                                      .outerjoin(Student_Lesson_Period, and_(subq_filter.c.student_id == Student_Lesson_Period.student_id,
                                                                             subq_filter.c.period_id == Student_Lesson_Period.period_id,
                                                                             Lesson.id == Student_Lesson_Period.lesson_id))
                                      .outerjoin(Student_Lesson_Period.score)
                                      .outerjoin(Score.score_type).group_by(Students.name, Class_room.class_room, Lesson.id, Lesson.lesson))
        subq = subq.subquery()

        base_q = (self.db.session.query(subq.c.name.label('name'),
                                        subq.c.class_room.label('class_room'),
                                        func.jsonb_object_agg(subq.c.lesson_id,
                                                              func.jsonb_build_object(subq.c.lesson, subq.c.avg)))
                                        .group_by(subq.c.name, subq.c.class_room)
                                        .order_by(subq.c.class_room).subquery())
        
        has_class_room = (self.db.session.query(literal(True)).filter(base_q.c.class_room.isnot(None)).exists())
        
        return (self.db.session.query(base_q).filter(or_(~has_class_room, base_q.c.class_room.isnot(None))).order_by(base_q.c.class_room).all())      

    def insert_student_lesson_year_for_retest(self, student_id, year_id):
        stmt = insert(Retest).from_select([Retest.lesson_id, 
                                           Retest.student_id, 
                                           Retest.year_id], select(Student_Lesson_Annual.lesson_id,
                                                                   literal(student_id),
                                                                   literal(year_id)).where(Student_Lesson_Annual.student_id == student_id,
                                                                                           Student_Lesson_Annual.year_id == year_id,
                                                                                           Student_Lesson_Annual.avg_annual < 5))
        stmt = stmt.on_conflict_do_nothing(index_elements=[Retest.lesson_id, Retest.student_id, Retest.year_id])
        self.db.session.execute(stmt)
    
    def insert_student_to_retest(self, student_id, lesson_id, year_id):
        self.db.session.add(Retest(student_id = student_id, lesson_id = lesson_id, year_id = year_id))

    def get_summary_result_for_class(self, data):
        return (self.db.session.query(func.jsonb_build_object('good', func.count(Student_Year_Summary.student_id).filter(Student_Year_Summary.learning_status == 'Tốt'),
                                      'fair', func.count(Student_Year_Summary.student_id).filter(Student_Year_Summary.learning_status == 'Khá'),
                                      'avg', func.count(Student_Year_Summary.student_id).filter(Student_Year_Summary.learning_status == 'Đạt'),
                                      'bad', func.count(Student_Year_Summary.student_id).filter(Student_Year_Summary.learning_status == 'Chưa đạt')))
                                      .filter(Student_Year_Summary.year_id == data['year_id'],
                                              Student_Year_Summary.class_room_id == data['class_room_id'])
                                      .group_by(Student_Year_Summary.class_room_id)
                                      .scalar())
    
    def get_student_summary_results_for_class(self, data):
        query = (self.db.session.query(Students.name,
                                       Students.student_code,
                                       Student_Year_Summary.score,
                                       Student_Year_Summary.conduct,
                                       Student_Year_Summary.learning_status, 
                                       Student_Year_Summary.status,
                                       Student_Year_Summary.note)
                                                .join(Students.student_year_summary)
                                                .filter(Student_Year_Summary.class_room_id == data['class_room_id'],
                                                        Student_Year_Summary.year_id == data['year_id'],
                                                        Student_Year_Summary.score.isnot(None)))
        
        if data.get('learning_status'):
            query = query.filter(Student_Year_Summary.learning_status == data['learning_status'])
        
        if data.get('status'):
            query = query.filter(Student_Year_Summary.status == data['status'])

        return query.order_by(Students.student_code).all()
    
    def get_students_for_retest(self, data):
        sub_student = (self.db.session.query(Retest.student_id.label('student_id'),
                                             Student_Year_Summary.class_room_id.label('class_room_id'),
                                             Student_Year_Summary.grade.label('grade'))
                                             .join(Student_Year_Summary, and_(Retest.student_id == Student_Year_Summary.student_id,
                                                                              Retest.year_id == Student_Year_Summary.year_id))
                                             .filter(Student_Year_Summary.year_id == data['year_id']))
        if data.get('grade'):
            sub_student = sub_student.filter(Student_Year_Summary.grade == data['grade'])
        if data.get('class_room_id'):
            sub_student = sub_student.filter(Student_Year_Summary.class_room_id == data['class_room_id'])
        if data.get('lesson_id'):
            sub_student = sub_student.filter(Retest.lesson_id == data['lesson_id'])
        
        sub_student = sub_student.distinct().subquery()
        
        sub_lesson = (self.db.session.query(Lesson.id.label('lesson_id'),
                                            Lesson.grade.label('grade'),
                                            Lesson.lesson.label('lesson')).join(Lesson.lessontag).filter(LessonTag.is_visible == True).subquery())
        
        frame = (self.db.session.query(sub_student.c.student_id.label('student_id'),
                                       sub_student.c.class_room_id.label('class_room_id'),
                                       sub_lesson.c.lesson_id.label('lesson_id'),
                                       sub_lesson.c.lesson.label('lesson')
                                       ).join(sub_student, sub_lesson.c.grade <= sub_student.c.grade).subquery())
        
        query = (self.db.session.query(frame.c.student_id,
                                       Students.name,
                                       Class_room.class_room,
                                       func.jsonb_object_agg(frame.c.lesson_id,
                                                             func.jsonb_build_object(frame.c.lesson, Retest.retest_score)),
                                       func.string_agg(func.distinct(case((Retest.lesson_id != None, frame.c.lesson),else_= None)), ', '))
                                       .join(Students, Students.id == frame.c.student_id)
                                       .join(Class_room, Class_room.id == frame.c.class_room_id)
                                       .outerjoin(Retest,
                                                  and_(frame.c.student_id == Retest.student_id,
                                                       frame.c.lesson_id == Retest.lesson_id,
                                                       Retest.year_id == data['year_id']))
                                       .group_by(frame.c.student_id, Students.name, Class_room.class_room)
                                       .order_by(Class_room.class_room, frame.c.student_id)
                                       .all())

        return query
    
    def get_retest_for_student(self, data):
        return (self.db.session.query(Retest).filter(Retest.student_id == data['student_id'],
                                                     Retest.lesson_id == data['lesson_id'],
                                                     Retest.year_id == data['year_id']).scalar())
    
    def update_retest_for_score(self, data):
        self.db.session.query(Retest).filter(Retest.student_id == data['student_id'],
                                             Retest.lesson_id == data['lesson_id'],
                                             Retest.year_id == data['year_id']).update({Retest.retest_score: data['score']})
    
    def check_retest_score_by_year(self, year_id):
        return (self.db.session.scalars(select(case((func.count(Retest.retest_score) == func.count(Retest.lesson_id), Retest.student_id), else_= None))
                        .filter(Retest.year_id == year_id)
                        .group_by(Retest.student_id)).all())
    
    def get_retest_score_by_year(self, year_id):
        return (self.db.session.query(Retest.student_id, func.array_agg(Retest.retest_score)).filter(Retest.year_id == year_id).group_by(Retest.student_id).all())
    
    def get_passed_score_by_year(self, year_id):
        return (self.db.session.query(Student_Year_Summary.student_id, func.array_agg(Student_Lesson_Annual.avg_annual))
                               .join(Student_Lesson_Annual, and_(Student_Lesson_Annual.student_id == Student_Year_Summary.student_id,
                                                                 Student_Lesson_Annual.year_id == Student_Year_Summary.year_id)) 
                               .filter(Student_Year_Summary.year_id == year_id,
                                       Student_Lesson_Annual.avg_annual >= 5,
                                       Student_Year_Summary.learning_status == 'Chưa đạt')
                               .group_by(Student_Year_Summary.student_id)
                               .all())
    
    def update_class_room_for_year_summary_by_student_year(self, data):
        self.db.session.query(Student_Year_Summary).filter(Student_Year_Summary.student_id == data['student_id'],
                                                           Student_Year_Summary.year_id == data['year_id']).update({Student_Year_Summary.class_room_id: data['class_room_id']})
        
    def update_class_room_for_period_summary_by_student_period(self, data):
        stmt = update(Student_Period_Summary).values({Student_Period_Summary.class_room_id: data['class_room_id']}).where(Student_Period_Summary.student_id == data['student_id'],
                                                                                                                          Student_Period_Summary.period_id == Period.id,
                                                                                                                          Period.year_id == data['year_id'])
        self.db.session.execute(stmt)
        
class AcademicTeacherRepo(BaseRepo):
    #Khu vực cho teacher
    def get_teaching_class_id_by_teacher_lesson_year(self, data: dict):
        return self.db.session.scalars(select(Teach_class.class_room_id).filter(Teach_class.year_id == data['year_id'],
                                                                                Teach_class.lesson_id == data['lesson_id'],
                                                                                Teach_class.teacher_id == data['teacher_id'])).all()
    
    def get_teacher_by_lesson_class_year(self, data: dict):    
        #teaching_class_ids, lesson_id, year_id
        return self.db.session.scalars(select(Teach_class.teacher_id).filter(Teach_class.class_room_id.in_(data['teaching_class_ids']), 
                                                                             Teach_class.lesson_id == data['lesson_id'],
                                                                             Teach_class.year_id == data['year_id'])).all()
    
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
    
    def get_teaching_class_by_teacher_year_general_folder(self, data):
        return (self.db.session.query(Teach_class).join(LessonTag, LessonTag.lesson_id == Teach_class.lesson_id)
                                                  .filter(Teach_class.teacher_id == data['teacher_id'],
                                                          Teach_class.year_id == data['year_id'],
                                                          LessonTag.is_folder == True,
                                                          LessonTag.is_visible == False).scalar())

    def get_user_by_student_id(self, data):
        return self.db.session.query(Users).join(Users.teachers).filter(Teachers.id == data['teacher_id']).scalar()
    
    def remove_teacher_from_teach_class_by_teacher_year(self, data):
        self.db.session.query(Teach_class).filter(Teach_class.year_id == data['year_id'],
                                                  Teach_class.teacher_id == data['teacher_id']).update({Teach_class.teacher_id: None})
        
    def get_teaching_class_to_assign_teacher(self, data):
        return self.db.session.query(Teach_class).filter(Teach_class.lesson_id == data['lesson_id'],
                                                         Teach_class.year_id == data['year_id'],
                                                         Teach_class.class_room_id.in_(data['teaching_class_ids'])).all()
    
    def update_teacher_to_teaching_class_by_class_year_lesson(self, data):
        self.db.session.query(Teach_class).filter(Teach_class.lesson_id == data['lesson_id'],
                                                  Teach_class.year_id == data['year_id'],
                                                  Teach_class.class_room_id.in_(data['class_room_ids'])).update({Teach_class.teacher_id: data['teacher_id']})
    
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
    
    def get_score(self, student_lesson_period_id, score_type_id, attempt):
        return (self.db.session.query(Score.score).filter(Score.attempt == attempt,
                                                          Score.score_type_id == score_type_id,
                                                          Score.student_lesson_period_id == student_lesson_period_id).scalar())

    def init_score_frame(self):
        return self.db.session.query(Score_Type.id, Score_Type.max_count).all()
    
    def get_score_by_student_lesson_period(self, data):
        return (self.db.session.query(cast(Student_Lesson_Period.student_id, String),
                                      cast(Score_Type.id, String),
                                      cast(Score.attempt, String),
                                      Score.score)
                                                .join(Student_Lesson_Period.period)
                                                .join(Student_Period_Summary, and_(Student_Period_Summary.student_id == Student_Lesson_Period.student_id,
                                                                                   Student_Period_Summary.period_id == Student_Lesson_Period.period_id))
                                                .outerjoin(Student_Lesson_Period.score)
                                                .outerjoin(Score.score_type)
                                                .filter(Student_Lesson_Period.lesson_id == data['lesson_id'],
                                                        Period.year_id == data['year_id'],
                                                        Period.semester_id == data['semester_id'],
                                                        Student_Period_Summary.class_room_id == data['class_room_id'])
                                                .all())
    
    def get_temp_summary_result_for_student_lesson_period(self, data):
        weighted_score = func.sum(Score.score * Score_Type.weight)
        total_weight = func.sum(Score_Type.weight)
        total = func.round(cast(weighted_score / total_weight, Numeric), 2)

        return (self.db.session.query(cast(Student_Lesson_Period.student_id, String),
                                      total)
                                      .join(Student_Lesson_Period.period)
                                      .join(Student_Period_Summary, and_(Student_Period_Summary.student_id == Student_Lesson_Period.student_id,
                                                                         Student_Period_Summary.period_id == Student_Lesson_Period.period_id))
                                      .outerjoin(Student_Lesson_Period.score)
                                      .outerjoin(Score.score_type)
                                      .filter(Period.year_id == data['year_id'],
                                              Period.semester_id == data['semester_id'],
                                              Student_Lesson_Period.lesson_id == data['lesson_id'],
                                              Student_Period_Summary.class_room_id == data['class_room_id'])
                                      .group_by(Student_Lesson_Period.student_id)
                                      .all())
    
    def get_summary_result_for_student_lesson_period(self, data):
        return self.db.session.query(cast(Student_Lesson_Period.student_id, String),
                                     Students.name,
                                     Student_Lesson_Period.total,
                                     Student_Lesson_Period.status,
                                     Student_Lesson_Period.note)\
                                        .join(Student_Lesson_Period.students)\
                                        .join(Student_Lesson_Period.period)\
                                        .join(Student_Period_Summary, and_(Student_Period_Summary.student_id == Student_Lesson_Period.student_id,
                                                                           Student_Period_Summary.period_id == Student_Lesson_Period.period_id))\
                                        .filter(Student_Lesson_Period.lesson_id == data['lesson_id'],
                                                Period.year_id == data['year_id'],
                                                Period.semester_id == data['semester_id'],
                                                Student_Period_Summary.class_room_id == data['class_room_id']).all()

    def get_score_type_ids(self):
        return self.db.session.scalars(select(Score_Type.id)).all()
    
    def upsert_score(self, data):
        stmt = insert(Score).values(**data)
        stmt = stmt.on_conflict_do_update(constraint='score_uniq',
                                          set_ = {'score': stmt.excluded.score},
                                          where = stmt.excluded.score.is_distinct_from(Score.score))
        
        self.db.session.execute(stmt)

    def get_exam_score(self, data):
        return self.db.session.query(Score.score).join(Score.score_type).filter(Score.student_lesson_period_id == data['student_lesson_period_id'],
                                                                                Score_Type.weight == 2).scalar()
    
    def get_final_exam_score(self, data):
        return self.db.session.query(Score.score).join(Score.score_type).filter(Score.student_lesson_period_id == data['student_lesson_period_id'],
                                                                                Score_Type.weight == 3).scalar()
    
    def get_total_rank_note_by_student_lesson_period(self, data):
        return self.db.session.query(Student_Lesson_Period.total,
                                     Student_Lesson_Period.status,
                                     Student_Lesson_Period.note).join(Student_Lesson_Period.period).filter(Student_Lesson_Period.student_id == data['student_id'],
                                                                                                           Student_Lesson_Period.lesson_id == data['lesson_id'],
                                                                                                           Period.year_id == data['year_id'],
                                                                                                           Period.semester_id == data['semester_id']).first()    
    
    # ket qua hoc tap cho hoc ky cua hoc sinh
    def get_avg_scores_for_students_by_lesson_class_and_period(self, data):
        weighted_score = func.sum(Score_Type.weight * Score.score)
        total_weight = func.sum(Score_Type.weight)
        avg_score = func.round(cast(weighted_score / total_weight, Numeric), 2)
        status = case((avg_score >= 5, True), else_ = False)

        return (self.db.session.query(Student_Lesson_Period.student_id,
                                      avg_score,
                                      status)
                                    .join(Student_Lesson_Period.score)
                                    .join(Score.score_type)
                                    .join(Student_Lesson_Period.period)
                                    .join(Student_Period_Summary, and_(Student_Period_Summary.student_id == Student_Lesson_Period.student_id,
                                                                        Student_Period_Summary.period_id == Student_Lesson_Period.period_id))
                                    .filter(Period.year_id == data['year_id'],
                                            Period.semester_id == data['semester_id'],
                                            Student_Period_Summary.class_room_id == data['class_room_id'],
                                            Student_Lesson_Period.lesson_id == data['lesson_id']).group_by(Student_Lesson_Period.student_id).all())

    def get_lessons_score_for_students_by_class_period(self, data):
        return (self.db.session.query(Student_Period_Summary.student_id,
                                      func.array_agg(Student_Lesson_Period.total))
                                      .join(Student_Lesson_Period, and_(Student_Lesson_Period.student_id == Student_Period_Summary.student_id,
                                                                        Student_Lesson_Period.period_id == Student_Period_Summary.period_id))
                                      .filter(Student_Period_Summary.period_id == data['period_id'],
                                              Student_Period_Summary.class_room_id == data['class_room_id'])
                                      .group_by(Student_Period_Summary.student_id)
                                      .all())

    def get_lessons_scores_by_student_period(self, data):
        return (self.db.session.query(cast(Student_Lesson_Period.lesson_id, String),
                                      cast(Score.score_type_id, String), cast(Score.attempt, String), Score.score)
                                      .join(Student_Lesson_Period.lesson)
                                      .join(Student_Lesson_Period.score)
                                      .join(Student_Lesson_Period.period)
                                      .filter(Period.year_id == data['year_id'],
                                              Period.semester_id == data['semester_id'],
                                              Student_Lesson_Period.student_id == data['student_id']).all())
    
    def get_lessons_by_student_id(self, data):
        return (self.db.session.query(Student_Period_Summary.student_id, cast(Lesson.id, String))
                                .join(Period, Period.id == Student_Period_Summary.period_id)
                                .join(Lesson, Student_Period_Summary.grade >= Lesson.grade)
                                .join(Lesson.lessontag)
                                .filter(Student_Period_Summary.student_id == data['student_id'],
                                        Period.year_id == data['year_id'],
                                        Period.semester_id == data['semester_id'],
                                        LessonTag.is_visible == True)
                                .all())
    
    def get_lessons_summary_by_student_period(self, data):
        return (self.db.session.query(cast(Student_Lesson_Period.lesson_id, String), 
                                      Lesson.lesson,
                                      Student_Lesson_Period.total,
                                      Student_Lesson_Period.status,
                                      Student_Lesson_Period.note)
                                      .join(Student_Lesson_Period.period)
                                      .join(Student_Lesson_Period.lesson)
                                      .filter(Period.year_id == data['year_id'],
                                              Period.semester_id == data['semester_id'],
                                              Student_Lesson_Period.student_id == data['student_id']).all())
    
class ScheduleRepo(BaseRepo):
    def bulk_upsert_schedule(self, data: dict):
        teacher_sub = select(Teach_class.teacher_id).where(Teach_class.class_room_id == data['class_room_id'],
                                                           Teach_class.lesson_id == data['lesson_id'],
                                                           Teach_class.year_id == data['year_id']).scalar_subquery()
        
        stmt = (insert(Schedule).from_select([Schedule.lesson_time,
                                              Schedule.day_of_week,
                                              Schedule.lesson_id,
                                              Schedule.period_id,
                                              Schedule.class_room_id,
                                              Schedule.teacher_id], select(literal(data['lesson_time']),
                                                                           literal(data['day_of_week']),
                                                                           literal(data['lesson_id']),
                                                                           literal(data['period_id']),
                                                                           literal(data['class_room_id']),
                                                                           teacher_sub)))

        stmt = stmt.on_conflict_do_update(constraint = 'schedule_uniq', 
                                          set_ = {'lesson_id': stmt.excluded.lesson_id,
                                                  'teacher_id': stmt.excluded.teacher_id},
                                          where = (stmt.excluded.lesson_id.is_distinct_from(Schedule.lesson_id) |
                                                   stmt.excluded.teacher_id.is_distinct_from(Schedule.teacher_id)))
        self.db.session.execute(stmt)

    def get_schedule_id(self, data):
        return self.db.session.query(Schedule.id).filter(Schedule.class_room_id == data['class_room_id'],
                                                         Schedule.period_id == data['period_id'],
                                                         Schedule.day_of_week == data['day_of_week'],
                                                         Schedule.lesson_time == data['lesson_time']).scalar()
    
    def get_schedules_by_class_period_lesson(self, data):
        return (self.db.session.scalars(select(Schedule).filter(Schedule.class_room_id == data['class_room_id'],
                                                                Schedule.lesson_id == data['lesson_id'],
                                                                Schedule.period_id == data['period_id'])).all())
    
    def remove_teacher_from_schedule_by_teacher_period_lesson(self, data):
        self.db.session.query(Schedule).filter(Schedule.teacher_id == data['teacher_id'],
                                               Schedule.period_id == data['period_id'],
                                               Schedule.lesson_id == data['lesson_id']).update({Schedule.teacher_id: None})
    
    def update_teacher_to_schedule_by_class_period_lesson(self, data):
        self.db.session.query(Schedule).filter(Schedule.class_room_id.in_(data['class_room_ids']),
                                               Schedule.period_id == data['period_id'],
                                               Schedule.lesson_id == data['lesson_id']).update({Schedule.teacher_id: data['teacher_id']})

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
    
    def get_schedule_for_class(self, data):
        return (self.db.session.query(Schedule.lesson_time,
                                      Schedule.day_of_week,
                                      cast(Schedule.lesson_id, String),
                                      Lesson.lesson).join(Schedule.lesson)
                                                    .join(Schedule.period)
                                                    .filter(Schedule.class_room_id == data['class_room_id'],
                                                            Period.year_id == data['year_id'],
                                                            Period.semester_id == data['semester_id']).order_by(Schedule.lesson_time).all())
    
    def get_teacher_id_by_lesson_and_class_room(self, data):
        return self.db.session.query(Teach_class.teacher_id).join(LessonTag, LessonTag.lesson_id == Teach_class.lesson_id)\
                                                            .filter(Teach_class.class_room_id == data['class_room_id'],
                                                                    Teach_class.lesson_id == data['lesson_id'],
                                                                    Teach_class.year_id == data['year_id'],
                                                                    LessonTag.is_visible == True).scalar()
    
    def get_schedule_for_teacher(self, data):
        return (self.db.session.query(Schedule.lesson_time,
                                      Schedule.day_of_week,
                                      cast(Schedule.class_room_id, String),
                                      Class_room.class_room).join(Class_room, Class_room.id == Schedule.class_room_id)
                                                            .join(Schedule.period)
                                                            .join(Teachers, Teachers.id == Schedule.teacher_id)
                                                            .filter(Period.year_id == data['year_id'],
                                                                    Period.semester_id == data['semester_id'],
                                                                    Teachers.user_id == data['user_id']).all())
    
    def get_schedule_for_admin(self, data):
        return (self.db.session.query(Schedule.lesson_time,
                                      Class_room.class_room,
                                      Lesson.lesson,
                                      Teachers.name).join(Schedule.lesson)
                                                    .outerjoin(Schedule.teachers)
                                                    .join(Class_room, Schedule.class_room_id == Class_room.id)
                                                    .join(Schedule.period)
                                                    .filter(Period.year_id == data['year_id'],
                                                            Period.semester_id == data['semester_id'],
                                                            Schedule.day_of_week == date.isoweekday(data['day'])).all())
    
    def get_schedules_by_teacher_and_day(self, data):
        return (self.db.session.query(Schedule.class_room_id,
                                      Class_room.class_room,
                                      func.array_agg(Schedule.lesson_time))
                                      .join(Schedule.period)
                                      .join(Schedule.teachers)
                                      .join(Class_room, Class_room.id == Schedule.class_room_id)
                                      .filter(Period.year_id == data['year_id'],
                                              Period.semester_id == data['semester_id'],
                                              Schedule.day_of_week == date.isoweekday(data['day']),
                                              Teachers.user_id == data['user_id'])
                                      .group_by(Schedule.class_room_id,
                                                Class_room.class_room).all())
    
    def get_schedule_id(self, data):
        return (self.db.session.query(Schedule.id).filter(Schedule.class_room_id == data['class_room_id'],
                                                          Schedule.day_of_week == date.isoweekday(data['day']),
                                                          Schedule.lesson_time == data['lesson_time']).scalar())
    
    def get_schedules_by_teacher_period(self, data):
        return self.db.session.scalars(select(Schedule)
                                       .join(Schedule.period)
                                       .filter(Schedule.teacher_id == data['teacher_id'], 
                                               Period.year_id == data['year_id'], 
                                               Period.semester_id == data['semester_id'])).all()

#############Attendence
    def upsert_attendence(self, data):
        stmt = insert(Attendence).values(**data)
        stmt = stmt.on_conflict_do_update(index_elements = [Attendence.student_id, Attendence.date],
                                          set_ = {Attendence.status: stmt.excluded.status,
                                                  Attendence.note: stmt.excluded.note},
                                          where = (or_(stmt.excluded.status.is_distinct_from(Attendence.status),
                                                       stmt.excluded.note.is_distinct_from(Attendence.note))))
        
        self.db.session.execute(stmt)
  
    def get_student_for_attendence_by_class_period(self, data):
        AttendenceToday = aliased(Attendence)
        return (self.db.session.query(Student_Period_Summary.student_id,
                                      Students.name,
                                      Attendence.date,
                                      Attendence.status,
                                      AttendenceToday.note)
                                                      .join(Student_Period_Summary.students)
                                                      .join(Period, Student_Period_Summary.period_id == Period.id)
                                                      .outerjoin(Attendence, and_(Attendence.student_id == Student_Period_Summary.student_id,
                                                                                  Attendence.period_id == Period.id,
                                                                                  Attendence.date.in_(data['dates'])))
                                                      .outerjoin(AttendenceToday, and_(AttendenceToday.student_id == Student_Period_Summary.student_id,
                                                                                       AttendenceToday.period_id == Period.id,
                                                                                       AttendenceToday.date == data['day']))
                                                      .filter(Student_Period_Summary.class_room_id == data['class_room_id'],
                                                              Period.semester_id == data['semester_id'],
                                                              Period.year_id == data['year_id'])
                                                      .all())
        