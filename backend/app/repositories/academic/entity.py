from app.models import Student_Lesson_Annual, Student_Lesson_Period, Student_Year_Summary, Class_room, \
                       Teach_class, Students, Score, Score_Type, Student_Period_Summary,\
                       Period, Users, Teachers, Lesson, Schedule, LessonTag, Attendence
from sqlalchemy import select, func, and_, text, cast, String, Numeric, true
from sqlalchemy.dialects.postgresql import insert
from ..base import BaseRepo
from datetime import date

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
    
    def get_class_room_by_student_period(self, data):
        return self.db.session.query(Class_room.id, Class_room.class_room).join(Class_room, Student_Period_Summary.class_room_id == Class_room.id,
                                                                                Period, Student_Period_Summary.period_id == Period.id).filter(Period.year_id == data['year_id'],
                                                                                                                                              Period.semester_id == data['semester_id'],
                                                                                                                                              Student_Period_Summary.student_id == data['student_id']).all()
    
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
        subq = self.db.session.query( Student_Year_Summary.student_id.label('student_id'),
                                      Student_Year_Summary.score.label('score'),
                                      Student_Year_Summary.conduct.label('conduct'),
                                      Student_Year_Summary.learning_status.label('learning_status'),
                                      Class_room.class_room.label('class_room'),
                                      Student_Year_Summary.note.label('note'),
                                      Student_Year_Summary.status.label('status')
                                      ).outerjoin(Class_room, Class_room.id == Student_Year_Summary.class_room_id).filter(Student_Year_Summary.year_id == data['prev_year_id'],
                                                                                                                          Student_Year_Summary.assign_status == data['assign_status']).subquery()
        
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
                                                            Student_Year_Summary.review_status == data['review_status']))

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
                                          set_ = {Student_Year_Summary.grade: stmt.excluded.grade},
                                          where = text('excluded.grade IS DISTINCT FROM student_year_summary.grade'))        
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
    
    ### Tong ket hoc ky
    def get_semester_lesson_total_by_student_for_class(self, data):
        weighted_score = func.sum(Score.score * Score_Type.weight)
        total_weight = func.sum(Score_Type.weight)
        total = func.round(cast(weighted_score / total_weight, Numeric), 2)
        return (self.db.session.query(Student_Lesson_Period.student_id,
                                      cast(Student_Lesson_Period.lesson_id, String),
                                      Lesson.lesson,
                                      total)
                                .join(Student_Lesson_Period.lesson)
                                .outerjoin(Student_Lesson_Period.score)
                                .join(Score.score_type)
                                .join(Student_Lesson_Period.period)
                                .join(Student_Period_Summary, and_(Student_Lesson_Period.student_id == Student_Period_Summary.student_id,
                                                                   Student_Lesson_Period.period_id == Student_Period_Summary.period_id))
                                .filter(Period.year_id == data['year_id'],
                                        Period.semester_id == data['semester_id'],
                                        Student_Period_Summary.class_room_id == data['class_room_id'])
                                .order_by(Student_Lesson_Period.student_id)
                                .group_by(Student_Lesson_Period.student_id,
                                          Student_Lesson_Period.lesson_id,
                                          Lesson.lesson)
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
                                      .filter(Student_Period_Summary.class_room_id == data['class_room_id'],
                                              Period.year_id == data['year_id'],
                                              Period.semester_id == data['semester_id'])
                                      .order_by(Student_Period_Summary.student_id)
                                      .all())
    
    ### Tong ket nam hoc
    def get_year_lesson_total_by_student_for_class(self, data):
        return (self.db.session.query(Student_Year_Summary.student_id,
                                      cast(Student_Lesson_Annual.lesson_id, String),
                                      Lesson.lesson,
                                      Student_Lesson_Annual.avg_annual)
                                      .outerjoin(Student_Lesson_Annual, and_(Student_Lesson_Annual.student_id == Student_Year_Summary.student_id,
                                                                             Student_Lesson_Annual.year_id == Student_Year_Summary.year_id))
                                      .outerjoin(Student_Lesson_Annual.lesson)
                                      .filter(Student_Year_Summary.class_room_id == data['class_room_id'])
                                      .order_by(Student_Year_Summary.student_id)
                                      .all())
    
    def get_student_year_summary_infos(self, data):
        return (self.db.session.query(Student_Year_Summary.student_id,
                                      Students.name,
                                      Student_Year_Summary.score,
                                      Student_Year_Summary.learning_status,
                                      Student_Year_Summary.conduct,
                                      Student_Year_Summary.absent_day,
                                      Student_Year_Summary.note)
                                      .join(Student_Year_Summary.students)
                                      .filter(Student_Year_Summary.year_id == data['year_id'],
                                              Student_Year_Summary.class_room_id == data['class_room_id'])
                                      .order_by(Student_Year_Summary.student_id)
                                      .all())

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
    
    def get_teaching_class_by_teacher_year_general_folder(self, data):
        return (self.db.session.query(Teach_class).join(LessonTag, LessonTag.lesson_id == Teach_class.lesson_id)
                                                  .filter(Teach_class.teacher_id == data['teacher_id'],
                                                          Teach_class.year_id == data['year_id'],
                                                          LessonTag.is_folder == True,
                                                          LessonTag.is_visible == False).scalar())

    def get_user_by_student_id(self, data):
        return self.db.session.query(Users).join(Users.teachers).filter(Teachers.id == data['teacher_id']).scalar()
    
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
    
    def get_score(self, data):
        return self.db.session.query(Score.score).join(Score.student_lesson_period)\
                                                 .join(Student_Lesson_Period.period)\
                                                        .filter(Score.attempt == data['attempt'],
                                                         Score.score_type_id == data['type_score_id'],
                                                         Student_Lesson_Period.student_id == data['student_id'],
                                                         Student_Lesson_Period.lesson_id == data['lesson_id'],
                                                         Period.year_id == data['year_id'],
                                                         Period.semester_id == data['semester_id']).scalar()

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
    
    def get_student_lesson_period_info(self, data):
        weighted_score = func.sum(Score.score * Score_Type.weight)
        total_weight = func.sum(Score_Type.weight)
        total = func.round(cast(weighted_score / total_weight, Numeric), 2)

        return (self.db.session.query(cast(Student_Lesson_Period.student_id, String),
                                      Students.name,
                                      total,
                                      Student_Lesson_Period.status,
                                      Student_Lesson_Period.note)
                                      .join(Student_Lesson_Period.period)
                                      .join(Student_Lesson_Period.students)
                                      .join(Student_Period_Summary, and_(Student_Period_Summary.student_id == Student_Lesson_Period.student_id,
                                                                         Student_Period_Summary.period_id == Student_Lesson_Period.period_id))
                                      .outerjoin(Student_Lesson_Period.score)
                                      .outerjoin(Score.score_type)
                                      .filter(Period.year_id == data['year_id'],
                                              Period.semester_id == data['semester_id'],
                                              Student_Lesson_Period.lesson_id == data['lesson_id'],
                                              Student_Period_Summary.class_room_id == data['class_room_id'])
                                      .group_by(Student_Lesson_Period.student_id,
                                                Students.name,
                                                Student_Lesson_Period.status,
                                                Student_Lesson_Period.note)
                                      .order_by(Student_Lesson_Period.student_id).all())
    
    def get_summary_result_for_student_lesson_period(self, data):
        return self.db.session.query(cast(Student_Lesson_Period.student_id, String),
                                     Students.name,
                                     Student_Lesson_Period.total,
                                     Student_Lesson_Period.status,
                                     Student_Lesson_Period.note)\
                                        .join(Student_Lesson_Period.students)\
                                        .join(Student_Lesson_Period.period)\
                                        .filter(Student_Lesson_Period.lesson_id == data['lesson_id'],
                                                Period.year_id == data['year_id'],
                                                Period.semester_id == data['semester_id']).all()

    def get_score_type_ids(self):
        return self.db.session.scalars(select(Score_Type.id)).all()
    
    def upsert_score(self, data):
        stmt = insert(Score).values(**data)
        stmt = stmt.on_conflict_do_update(index_elements = [Score.student_lesson_period_id, Score.score_type_id, Score.attempt],
                                          set_ = {'score': stmt.excluded.score},
                                          where = text('excluded.score IS DISTINCT FROM score.score'))
        
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
        avg_score = weighted_score / total_weight
        avg_score = func.round(cast(weighted_score / total_weight, Numeric), 2)

        return (self.db.session.query(Student_Lesson_Period.student_id,
                                      avg_score).join(Student_Lesson_Period.score)
                                                .join(Score.score_type)
                                                .join(Student_Lesson_Period.period)
                                                .join(Student_Period_Summary, and_(Student_Period_Summary.student_id == Student_Lesson_Period.student_id,
                                                                                    Student_Period_Summary.period_id == Student_Lesson_Period.period_id))
                                                .filter(Period.year_id == data['year_id'],
                                                        Period.semester_id == data['semester_id'],
                                                        Student_Period_Summary.class_room_id == data['class_room_id'],
                                                        Student_Lesson_Period.lesson_id == data['lesson_id']).group_by(Student_Lesson_Period.student_id).all())

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
    
    def get_weak_students(self, data):
        subq_filter = (self.db.session.query(Student_Lesson_Period.student_id.label('student_id'))
                                                    .join(Student_Lesson_Period.period)
                                                    .join(Student_Lesson_Period.score)
                                                    .join(Score.score_type)
                                                    .filter(Period.year_id == data['year_id'],
                                                            Period.semester_id == data['semester_id'])
                                                    .group_by(Student_Lesson_Period.student_id,
                                                              Student_Lesson_Period.lesson_id)
                                                    .having(func.sum(Score.score * Score_Type.weight) / func.sum(Score_Type.weight) < 5)
                                                    .distinct()
                                                    .subquery())
        
        subq = (self.db.session.query(subq_filter.c.student_id.label('student_id'),
                                      Students.name.label('name'),
                                      Class_room.class_room.label('class_room'),
                                      Student_Lesson_Period.lesson_id.label('lesson_id'),
                                      Lesson.lesson.label('lesson'),
                                      (func.sum(Score.score * Score_Type.weight) / func.sum(Score_Type.weight)).label('avg'))
                                      .join(Student_Lesson_Period, Student_Lesson_Period.student_id == subq_filter.c.student_id)
                                      .join(Student_Lesson_Period.students)
                                      .join(Student_Period_Summary, and_(Student_Period_Summary.student_id == Student_Lesson_Period.student_id,
                                                                         Student_Period_Summary.period_id == Student_Lesson_Period.period_id))
                                      .join(Class_room, Student_Period_Summary.class_room_id == Class_room.id)
                                      .join(Student_Lesson_Period.period)
                                      .join(Student_Lesson_Period.lesson)
                                      .outerjoin(Student_Lesson_Period.score)
                                      .outerjoin(Score.score_type)
                                      .filter(Period.year_id == data['year_id'],
                                              Period.semester_id == data['semester_id'])
                                      .group_by(subq_filter.c.student_id,
                                                Students.name,
                                                Class_room.class_room,
                                                Student_Lesson_Period.lesson_id,
                                                Lesson.lesson).subquery())
        
        return (self.db.session.query(subq.c.name,
                                      subq.c.class_room,
                                      func.jsonb_object_agg(subq.c.lesson_id,
                                                            func.jsonb_build_object(subq.c.lesson, subq.c.avg)))
                                      .group_by(subq.c.name,
                                                subq.c.class_room)
                                      .order_by(subq.c.class_room).all())
    
class ScheduleRepo(BaseRepo):
    def bulk_upsert_schedule(self, data: dict):
        stmt = insert(Schedule).values(**data)
        stmt = stmt.on_conflict_do_update(index_elements = [Schedule.class_room_id, 
                                                            Schedule.period_id, 
                                                            Schedule.day_of_week, 
                                                            Schedule.lesson_time], 
                                          set_ = {'lesson_id': stmt.excluded.lesson_id},
                                          where = text("excluded.lesson_id IS DISTINCT FROM schedule.lesson_id"))
        self.db.session.execute(stmt)

    def get_schedule_id(self, data):
        return self.db.session.query(Schedule.id).filter(Schedule.class_room_id == data['class_room_id'],
                                                         Schedule.period_id == data['period_id'],
                                                         Schedule.day_of_week == data['day_of_week'],
                                                         Schedule.lesson_time == data['lesson_time']).scalar()
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
                                                            Schedule.day_of_week == date.today().isoweekday()).all())
    
    def get_lesson_time_by_class_day(self, data):
        sub = (self.db.session.query(Students.name.label('name'),
                                     Student_Period_Summary.student_id.label('student_id'))
                                     .join(Students.student_period_summary)
                                     .join(Period, Period.id == Student_Period_Summary.period_id)
                                     .filter(Period.year_id == data['year_id'],
                                             Period.semester_id == data['semester_id'],
                                             Student_Period_Summary.class_room_id == data['class_room_id'])
                                     .order_by(Student_Period_Summary.student_id).subquery())
        
        return (self.db.session.query(sub.c.name,
                                      sub.c.student_id,
                                      func.jsonb_object_agg(Schedule.lesson_time,
                                      func.jsonb_build_object(Lesson.lesson, Attendence.status)),
                                      func.aggregate_strings(Attendence.note, ", ").filter(Attendence.note != ''))
                                      .join(Schedule.period)
                                      .join(Schedule.lesson)
                                      .join(sub, true())
                                      .outerjoin(Attendence, and_(Attendence.schedule_id == Schedule.id,
                                                                  Attendence.student_id == sub.c.student_id))
                                      .filter(Period.year_id == data['year_id'],
                                              Period.semester_id == data['semester_id'],
                                              Schedule.day_of_week == date.today().isoweekday(),
                                              Schedule.class_room_id == data['class_room_id'])
                                      .group_by(sub.c.name, sub.c.student_id).all())
    
    def get_schedules_by_teacher_and_day(self, data):
        return (self.db.session.query(Schedule.class_room_id,
                                      Class_room.class_room,
                                      func.array_agg(Schedule.lesson_time))
                                      .join(Schedule.period)
                                      .join(Schedule.teachers)
                                      .join(Class_room, Class_room.id == Schedule.class_room_id)
                                      .filter(Period.year_id == data['year_id'],
                                              Period.semester_id == data['semester_id'],
                                              Schedule.day_of_week == date.today().isoweekday(),
                                              Teachers.user_id == data['user_id'])
                                      .group_by(Schedule.class_room_id,
                                                Class_room.class_room).all())
    
    def get_schedule_id(self, data):
        return (self.db.session.query(Schedule.id).filter(Schedule.class_room_id == data['class_room_id'],
                                                          Schedule.day_of_week == date.isoweekday(data['day']),
                                                          Schedule.lesson_time == data['lesson_time']).scalar())
    
    def create_attendence(self, data):
        self.db.session.add(Attendence(**data))


    def upsert_attendence(self,data):
        stmt = insert(Attendence).values(**data)
        stmt = stmt.on_conflict_do_update(index_elements = [Attendence.student_id, Attendence.schedule_id],
                                          set_ = {'status': stmt.excluded.status,
                                                  'note': stmt.excluded.note},
                                          where = text('excluded.status IS DISTINCT FROM attendence.status OR excluded.note IS DISTINCT FROM attendence.note'))
        
        self.db.session.execute(stmt)