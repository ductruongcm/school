from ..validation import Academic_Teacher_Validation, Academic_Validation
from .core import AcademicGetService
from app.utils import filter_fields
from app.exceptions import NotFound_Exception
import logging

logger = logging.getLogger(__name__)

class Academic_Teacher_Service:
    def __init__(self, db, repo):
        self.repo = repo(db)
        self.academic_teacher_repo = self.repo.academic_teacher
        self.academic_teacher_validation = Academic_Teacher_Validation(db, repo)

    def handle_remove_home_class(self, data):
        #check có homeclass chưa
        home_class = self.academic_teacher_repo.get_home_class_by_teacher_and_year({'teacher_id': data['teacher_id'],
                                                                            'year_id': data['year_id']})
        if not home_class:
            raise NotFound_Exception('Không tìm thấy lớp học từ ID teacher và ID year!')
        
        home_class.teacher_id = None

    def handle_update_teaching_class_by_lesson(self, data):
        #get all of teach class by teacher, year
        teaching_classes = self.academic_teacher_repo.get_teaching_class_by_teacher_year({'teacher_id': data['teacher_id'],
                                                                                'year_id': data['year_id']})
        for teaching_class in teaching_classes:
            teaching_class.teacher_id = None

    def handle_update_teaching_class(self, data):
        new_teach_rooms = set(data.get('teach_class'))
        current_teach_rooms = set(self.academic_teacher_repo.get_teaching_class_id_by_teacher({'teacher_id': data['teacher_id'],
                                                                                  'year_id': data['year_id'],
                                                                                  'lesson_id': data['lesson_id']}))
        if to_add := new_teach_rooms - current_teach_rooms:
            #check dup
            self.academic_teacher_validation.check_existing_teacher_in_teaching_class({'teaching_class_ids': to_add,
                                                                                          'year_id': data['year_id'],
                                                                                          'lesson_id': data['lesson_id']})
            #add teacher_id to teaching class
            teaching_classes = self.academic_teacher_repo.get_teaching_class_to_assign_teacher({'teaching_class_ids': to_add,
                                                                                      'year_id': data['year_id'],
                                                                                      'lesson_id': data['lesson_id']})
            for teaching_class in teaching_classes:
                teaching_class.teacher_id = data['teacher_id']
        
        if to_del:= current_teach_rooms - new_teach_rooms:
            teaching_classes = self.academic_teacher_repo.get_teaching_class_to_remove_teacher({'teacher_id': data['teacher_id'],
                                                                                      'year_id': data['year_id'],
                                                                                      'teaching_class_ids': to_del})
            
            for teaching_class in teaching_classes:
                teaching_class.teacher_id = None

class Academic_Student_Service:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.academic_student_repo = self.repo.academic_student
        self.academic_get_service = AcademicGetService(db, repo)
        self.academic_validation = Academic_Validation(db, repo)
        
    def get_student_year_summary(self, data):
        student_year_summary = self.academic_student_repo.get_student_year_summary({'student_id': data['student_id'],
                                                                                    'year_id': data['year_id']})
        if not student_year_summary:
            raise NotFound_Exception('Không tìm thấy student year summary!')
        
        return student_year_summary
    
    def handle_get_students_by_period_and_class_room(self, data):
        student_ids = self.academic_student_repo.get_student_ids_by_period_and_class_room(data)

        if not student_ids:
            raise NotFound_Exception('Không tìm thấy student ids!')
        
        return student_ids

    def handle_add_student_grade_year_to_student_class(self, data):
        self.academic_student_repo.insert_student_grade_year_to_student_class({'student_id': data['student_id'],
                                                                               'grade': data['grade'],
                                                                               'year_id': data['year_id']})
        
    def handle_add_student_year_summary(self, data):
        self.academic_student_repo.insert_student_year_summary(data)
        
    def handle_add_student_period_summary(self, data):
        self.academic_student_repo.insert_student_period_summary(data)

    def handle_add_student_lesson_annual(self, data):
        self.academic_student_repo.insert_student_lesson_annual(data)
        
    def handle_add_student_lesson_period(self, data):
        self.academic_student_repo.insert_student_lesson_period({'student_id': data['student_id'],
                                                                 'period_id': data['period_id'],
                                                                 'lesson_id': data['lesson_id']})
            
    def record_academic_results_for_semester(self, student_id, lesson_id, year_id, semester_id, total):
        period_id = self.academic_get_service.handle_get_period_id({'year_id': year_id,'semester_id': semester_id})
        status = 'Đạt' if total >=5 else 'Không đạt'
        self.academic_student_repo.insert_student_lesson_period({'student_id': student_id,
                                                                 'lesson_id': lesson_id,
                                                                 'period_id': period_id,
                                                                 'total': total,
                                                                 'status': status})        
    
    def record_academic_annual_results(self, student_id, lesson_id, year_id, total_1, total_2):
        avg_annual = round((total_2*2 + total_1)/3, 2)
        status = 'Đạt' if avg_annual >= 5 else 'Không đạt'
        self.academic_student_repo.insert_student_lesson_annual({'student_id': student_id,
                                                                 'year_id': year_id,
                                                                 'lesson_id': lesson_id,
                                                                 'avg_annual': avg_annual,
                                                                 'status': status})
        
    def handle_record_academic_annual_result(self, data):
        self.academic_validation.validate_year_id(data)

        query = self.academic_student_repo.get_scores_for_year_summary(data)
        for item in query:
            student_id = item[0]
            for lessons in item[1].values():
                lesson_ids = list(lessons.keys())

            for lesson_id in lesson_ids:
                self.record_academic_annual_results(student_id, lesson_id, data['year_id'], item[1].get('1')[lesson_id], item[1].get('2')[lesson_id])

    def handle_record_prev_year_academic_semesters_results(self, raw_data):
        year_id = raw_data['year_id']
        student_id = raw_data['student_id']
        for data in raw_data['lesson']:
            self.record_academic_annual_results(student_id, data['lesson_id'], year_id, data['score_1'], data['score_2'])
            for semester_id in [1,2]:
                self.record_academic_results_for_semester(student_id, data['lesson_id'], year_id, semester_id, data[f'score_{semester_id}'])

    def handle_record_prev_year_academic_year_result(self, raw_data):
        #Dành cho học sinh chưa có trong hệ thống
        data = filter_fields('student_id', 'grade', 'year_id', 'conduct', 'absent_day', 'note', 'class_room_id', context = raw_data)
        lesson_totals = self.academic_student_repo.get_annual_lesson_totals_by_student_and_year({'student_id': data['student_id'], 'year_id': data['year_id']})
        learning_status, score = self.rank_academic_result(lesson_totals)

        data.update({'learning_status': learning_status, 'score': score})
        self.academic_student_repo.insert_student_year_summary(data)

    def rank_academic_result(self, lesson_scores):
        #lấy điểm TB tất cả các môn cả năm của học sinh(ko phân biệt môn)
        avg_score = round(sum(lesson_scores)/len(lesson_scores), 2)
   
        if all(score >= 6.5 for score in lesson_scores) and sum(1 for score in lesson_scores if score >= 8) >= 6:
            learning_status = 'Tốt'
            
        elif all(score >= 5 for score in lesson_scores) and sum(1 for score in lesson_scores if score >= 6.5) >= 6:
            learning_status = 'Khá'

        elif all(score >= 3.5 for score in lesson_scores) and sum(1 for score in lesson_scores if score < 5) <= 1 and sum(1 for score in lesson_scores if score >= 5) >= 6:
            learning_status = 'Trung bình'

        elif sum(1 for score in lesson_scores if score < 5) >= 3 or sum(1 for score in lesson_scores if score < 3.5) >= 1:
            learning_status = 'Không đạt'
  
        return learning_status, avg_score                
    
    def handle_record_academic_year_result(self, data):
        lesson_totals = self.academic_student_repo.get_year_lesson_totals_by_student_and_year(data)

        learning_status, score = self.rank_academic_result(lesson_totals)

        student_period_summary = self.academic_student_repo.get_student_year_summary(data)
        student_period_summary.score = score
        student_period_summary.learning_status = learning_status
        student_period_summary.conduct = data['conduct']
        student_period_summary.absent_day = data['absent_day']
        student_period_summary.note = data['note']

    def handle_record_academic_semester_results(self, data):
        #get less result add stu per sum 
        lesson_totals = self.academic_student_repo.get_semester_lesson_totals_by_student_and_period(data)
        learning_status, score = self.rank_academic_result(lesson_totals)

        student_period_summary = self.academic_student_repo.get_student_period_summary(data)
        student_period_summary.score = score
        student_period_summary.status = learning_status
        student_period_summary.conduct = data['conduct']
        student_period_summary.absent_day = data['absent_day']
        student_period_summary.note = data['note']
    
    def handle_review_students(self, data):
        #summary year by student
        student_year_summary = self.get_student_year_summary(data)
        student_year_summary.status = data['status']
        student_year_summary.review_status = True

    def handle_update_student_assign_status(self, data):
        data['year_id'] = self.academic_get_service.handle_get_prev_year_id(data)
        student_year_summary = self.get_student_year_summary(data)
        student_year_summary.assign_status = True

    def handle_get_student_lesson_period(self, data):
        student_lesson_period = self.academic_student_repo.get_student_lesson_period(data)
        if not student_lesson_period:
            raise NotFound_Exception('Không tìm thấy student_lesson_period!')
        
        return student_lesson_period
    
    def handle_show_students_by_class_lesson_period(self, data):
        result = self.academic_student_repo.show_students_by_class_lesson_period(data)
        return result
    
    def handle_show_student_for_semester_summary(self, data):
        result = self.academic_student_repo.show_students_for_semester_summary(data)

        keys = ['student_id', 'name', 'scores', 'total', 'status', 'conduct', 'absent_day', 'note']
        return [dict(zip(keys, values)) for values in result]
    
    def handle_show_student_for_year_summary(self, data):
        result = self.academic_student_repo.show_students_for_year_summary(data)
        keys = ['student_id', 'name', 'scores', 'total', 'status', 'conduct', 'absent_day', 'note']
        return [dict(zip(keys, values)) for values in result]

    def handle_show_students_for_class_assignment(self, data: dict): # for assign student to class
        result = self.academic_student_repo.show_students_for_class_assignment(data)
        keys = ['student_id', 'student_code', 'name', 'score', 'conduct', 'learning_status', 'absent_day', 'class_room_id', 'note', 'status', 'grade', 'review_status']
        return [dict(zip(keys, values)) for values in result]

class Academic_Score_Service:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.academic_score_repo = self.repo.score
        self.academic_get_service = AcademicGetService(db, repo)
        self.academic_validation = Academic_Validation(db, repo)

    def handle_upsert_score(self, data):
        scores = []
        for score_type_id, score in data['scores'].items():
            for attempt in score.keys():
                self.academic_score_repo.upsert_score({'student_lesson_period_id': data['student_lesson_period_id'],
                                                       'score_type_id': score_type_id,
                                                       'attempt': attempt,
                                                       'score': score[attempt]})

                scores.append(score[attempt])
        return scores

    def handle_show_scores_by_students(self, data, students):
        output = []
        for student in students:
            _dict = {'student_id': student[0],
                     'name': student[1],
                     'scores': self.init_score_frame(student[0], data['period_id'], data['lesson_id']),
                     'note': student[4],
                     'total': student[2],
                     'status': student[3]}
            
            output.append(_dict)
       
        return output
    
    def init_score_frame(self, student_id, period_id, lesson_id):
        result = self.academic_score_repo.init_score_frame()
        score_frame = {}
        for r in result:
            key = str(r[0])
            attempts = {}

            for att in range(r[1]):
                score = self.academic_score_repo.get_score(student_id, period_id, lesson_id, attempt = att + 1, type_score_id = r[0])
                attempts[str(att + 1)] = score
            
            score_frame[key] = attempts

        return score_frame  
    
    def handle_get_scores_and_status_for_student_lesson_period(self, student_lesson_period_id):
        r = self.academic_score_repo.get_scores_by_student_lesson_period_id(student_lesson_period_id)
        score = (sum(r[0][1]) + r[1][1][0] * r[1][0] + r[2][1][0] * r[2][0]) / (len(r[0][1]) + r[1][0] + r[2][0])
        score = round(score, 2)
        status = self.ranking_for_score(score)
        return score, status
    
    def ranking_for_score(self, score):
        if score >= 9:
            status = 'Giỏi'
        
        elif score > 6.5:
            status = 'Tốt'

        elif score >= 5:
            status = 'Trung bình'

        else:
            status = 'Không đạt'

        return status

class Academic_Schedule_Service:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.schedule_repo = self.repo.schedule
        self.academic_get_service = AcademicGetService(db, repo)
   
    def handle_show_schedules(self, data):
        period_id = self.academic_get_service.handle_get_period_id(data)
        frame = {}
        for period in range(5):
            lesson_time = {}
            period = str(period + 1)
            for day_of_week in range(6):
                day_of_week += 1
                raw_lessons = self.schedule_repo.show_lesson_for_schedules(period_id, data['class_room_id'], day_of_week, period) or []

                if raw_lessons:
                    raw_lesson = raw_lessons[0]
                    lesson = {'lesson_id': int(raw_lesson[0]), 'lesson': raw_lesson[1]}
                else:
                    lesson = {'lesson_id': None, 'lesson': None}

                lesson_time[str(day_of_week)] = lesson

            frame[period] = lesson_time

        return frame
     
    def handle_add_schedule(self, data, user_id):
        period_id = self.academic_get_service.handle_get_period_id(data)

        for lesson_time, day_lesson in data['schedules'].items():
            for day, values in day_lesson.items():
                for lesson in values.values():
                    insert_data = {'lesson_time': lesson_time,
                                   'day_of_week': day,
                                   'period_id': period_id,
                                   'class_room_id': data['class_room_id']}
                    
                    if lesson is None:
                        self.schedule_repo.delete_schedule(insert_data)
                    
                    else:
                        insert_data.update({'lesson_id': lesson})
                        self.schedule_repo.bulk_upsert_schedule(insert_data)
        
        self.db.session.commit()

           
                

      


    