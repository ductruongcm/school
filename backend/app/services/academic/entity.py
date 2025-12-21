from ..validation import Academic_Teacher_Validation, Academic_Validation
from collections import defaultdict
from .core import AcademicGetService
from app.utils import filter_fields
from app.exceptions import NotFound_Exception, CustomException, DuplicateException
from ..log import ActivityLog_Service
from ..student import StudentServices
import pandas as pd
import numpy as np
from datetime import timedelta

class Academic_Teacher_Service:
    def __init__(self, db, repo):
        self.repo = repo(db)
        self.academic_teacher_repo = self.repo.academic_teacher
        self.schedule_repo = self.repo.schedule
        self.academic_teacher_validation = Academic_Teacher_Validation(db, repo)

    def handle_remove_home_class(self, data):
        #check có homeclass chưa
        home_class = self.academic_teacher_repo.get_home_class_by_teacher_and_year({'teacher_id': data['teacher_id'],
                                                                                    'year_id': data['year_id']})
        if home_class:
            home_class.teacher_id = None

        teach_class = self.academic_teacher_repo.get_teaching_class_by_teacher_year_general_folder(data)
        if teach_class:
            teach_class.teacher_id = None

    def handle_get_user_by_teacher_id(self, data):
        user = self.academic_teacher_repo.get_user_by_student_id(data)
        if not user:
            raise NotFound_Exception('Không tìm thấy user!')
        
        return user

    def handle_remove_teacher_from_teaching_class(self, data):
        #get all of teach class by teacher, year
        self.academic_teacher_repo.remove_teacher_from_teach_class_by_teacher_year({'teacher_id': data['teacher_id'],
                                                                                    'year_id': data['year_id']})

    def handle_update_teaching_class(self, data):
        new_teach_rooms = set(data.get('teach_class'))

        current_teach_rooms = set(self.academic_teacher_repo.get_teaching_class_id_by_teacher_lesson_year({'teacher_id': data['teacher_id'],
                                                                                                           'year_id': data['year_id'],
                                                                                                           'lesson_id': data['lesson_id']}))
        if to_add := new_teach_rooms - current_teach_rooms:
            #check dup
            self.academic_teacher_validation.check_existing_teacher_in_teaching_classes({'teaching_class_ids': to_add,
                                                                                          'year_id': data['year_id'],
                                                                                          'lesson_id': data['lesson_id']})
            #update teacher_id to teaching class
            self.academic_teacher_repo.update_teacher_to_teaching_class_by_class_year_lesson({'class_room_ids': to_add,
                                                                                              'year_id': data['year_id'],
                                                                                              'lesson_id': data['lesson_id'],
                                                                                              'teacher_id': data['teacher_id']})
            #update teacher_id to schedule
            self.schedule_repo.update_teacher_to_schedule_by_class_period_lesson({'class_room_ids': to_add,
                                                                                  'period_id': data['period_id'],
                                                                                  'lesson_id': data['lesson_id'],
                                                                                  'teacher_id': data['teacher_id']})

        
        if to_del:= current_teach_rooms - new_teach_rooms:
            self.academic_teacher_repo.update_teacher_to_teaching_class_by_class_year_lesson({'class_room_ids': to_del,
                                                                                              'year_id': data['year_id'],
                                                                                              'lesson_id': data['lesson_id'],
                                                                                              'teacher_id': None})
            
            self.schedule_repo.update_teacher_to_schedule_by_class_period_lesson({'class_room_ids': to_del,
                                                                                  'period_id': data['period_id'],
                                                                                  'lesson_id': data['lesson_id'],
                                                                                  'teacher_id': None})


class Academic_Student_Service:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.academic_student_repo = self.repo.academic_student
        self.student_service = StudentServices(db, repo)
        self.academic_get_service = AcademicGetService(db, repo)
        self.academic_validation = Academic_Validation(db, repo)
        self.activity_log_service = ActivityLog_Service(db, repo)
        
    def get_student_year_summary(self, data):
        student_year_summary = self.academic_student_repo.get_student_year_summary({'student_id': data['student_id'],
                                                                                    'year_id': data['year_id']})
        if not student_year_summary:
            raise NotFound_Exception('Không tìm thấy student year summary!')
        
        return student_year_summary
    
    def handle_get_class_room_by_student_period(self, data):
        class_room_id, class_room = self.academic_student_repo.get_class_room_by_student_period(data)
        if not class_room_id or not class_room:
            raise NotFound_Exception('Không tìm thấy class room!')
        
        return class_room_id, class_room
    
    def handle_get_students_by_period_and_class_room(self, data):
        student_ids = self.academic_student_repo.get_student_ids_by_period_and_class_room(data)

        if not student_ids:
            raise NotFound_Exception('Không tìm thấy student ids!')
        
        return student_ids

    def handle_add_student_grade_year_to_student_class(self, data):
        self.academic_student_repo.insert_student_grade_year_to_student_class({'student_id': data['student_id'],
                                                                               'grade': data['grade'],
                                                                               'year_id': data['year_id']})
        
    def handle_add_student_period_summary_for_new_year(self, data):
        self.academic_student_repo.insert_student_period_summary_for_new_year(data)

    def handle_add_student_lesson_period_for_new_year(self, data):
        self.academic_student_repo.insert_student_lesson_period_for_new_year(data)
    
#####################################################################
#add kết quả từng môn cho từng học kỳ và cả năm của năm cũ cho học sinh mới **** Từng môn học
    def handle_record_prev_year_lessons_result(self, data):
        annual_result = []
        period_result = []
        period_ids = self.academic_get_service.handle_get_period_ids_by_year(data)

        period_map = {'period_id_1': min(period_ids),
                      'period_id_2': max(period_ids)}
        
        for lesson_score in data['lesson']:
            avg_annual = round((lesson_score['score_1'] + lesson_score['score_2'] * 2) / 3, 2)
            annual_result.append({'student_id': data['student_id'],
                                  'lesson_id': lesson_score['lesson_id'],
                                  'year_id': data['year_id'],
                                  'avg_annual': avg_annual,
                                  'status': True if avg_annual >= 5 else False})
            
            period_result.extend([{
                                    'student_id': data['student_id'],
                                    'lesson_id': lesson_score['lesson_id'],
                                    'period_id': period_map['period_id_1'],
                                    'total': lesson_score['score_1'],
                                    'status': True if lesson_score['score_1'] >= 5 else False
                                  }, 
                                  {
                                    'student_id': data['student_id'],
                                    'lesson_id': lesson_score['lesson_id'],
                                    'period_id': period_map['period_id_2'],
                                    'total': lesson_score['score_2'],
                                    'status': True if lesson_score['score_2'] >= 5 else False}])
            
        self.academic_student_repo.upsert_student_lesson_period(period_result)    
        self.academic_student_repo.upsert_student_lesson_annual(annual_result)       
    
#add tổng kết cho từng học kỳ và cả năm của năm cũ cho học sinh mới
    def handle_record_prev_year_academic_semesters_summary(self, data):
        lesson_totals = self.academic_student_repo.get_semester_lesson_totals_by_student_and_period({'student_id': data['student_id'],
                                                                                                     'year_id': data['year_id']})
        
        df = pd.DataFrame(lesson_totals, columns=['period_id', 'scores'])
        matrix_scores = np.array(df['scores'].to_list(), dtype=float)
        
        conditions = self.ranking_for_summary(matrix_scores)
        choices = ['Tốt', 'Khá', 'Đạt']

        df['status'] = np.select(conditions, choices, default='Chưa đạt')
        df['score'] = np.round(matrix_scores.mean(axis=1), 2)
        flat_dicts = df.drop(columns='scores').to_dict(orient='records')

        for period_result in flat_dicts:
            self.academic_student_repo.insert_student_period_summary({'student_id': data['student_id'],
                                                                      'period_id': period_result['period_id'],
                                                                      'grade': data['grade'],
                                                                      'status': period_result['status'],
                                                                      'score': period_result['score']})
            
    def handle_record_prev_year_academic_year_summary(self, raw_data):
        #Dành cho học sinh chưa có trong hệ thống
        data = filter_fields('student_id', 'grade', 'year_id', 'conduct', 'absent_day', 'note', 'class_room_id', 'transfer_info', context = raw_data)
        scores = self.academic_student_repo.get_annual_lesson_totals_by_student_and_year({'student_id': data['student_id'], 'year_id': data['year_id']})
        scores_matrix = np.atleast_2d(np.array(scores, dtype=float))
  
        conditions = self.ranking_for_summary(scores_matrix)
        choices = ['Tốt', 'Khá', 'Đạt']

        learning_status = np.select(conditions, choices, default='Chưa đạt')
        score = np.round(scores_matrix.mean(axis=1))
        data.update({'learning_status': learning_status.item(), 'score': float(score.item())})
        data['is_new_student'] = True
        self.academic_student_repo.insert_student_year_summary(data)
       
#################################################    
#Tong ket hoc ky
    def handle_show_student_for_semester_summary(self, data):
        info = self.academic_student_repo.get_student_semester_summary_infos(data)
        info_df = pd.DataFrame(info, columns = ['student_id', 'name','score', 'status', 'conduct', 'absent_day', 'note'])
        if info_df['score'].isna().any():
            temp_info = self.academic_student_repo.get_temp_student_semester_summary_infos(data)
            info_df = pd.DataFrame(temp_info, columns = ['student_id', 'name','score', 'status', 'conduct', 'absent_day', 'note'])
        
        student_lesson_total = self.academic_student_repo.get_semester_lesson_total_by_student_for_class(data)
        final_df = pd.DataFrame(student_lesson_total, columns=['student_id', 'lessons'])

        output = final_df.merge(info_df, on = 'student_id', how = 'left').replace({np.nan: None}).to_dict('records')

        return output

    def record_academic_results_for_semester(self, data):
        students = self.academic_student_repo.get_avg_for_student_lesson_period(data)
        df = pd.DataFrame(students, columns=['student_id', 'scores', 'score'])

        if df['scores'].apply(lambda x: any(v is None for v in x)).any():
            raise CustomException('Còn môn học chưa tổng kết!')
        
        data['period_id'] = self.academic_get_service.handle_get_period_id(data)

        matrix_scores = np.array(df['scores'].to_list(), dtype=float)

        conditions = self.ranking_for_summary(matrix_scores)
        choices = ['Tốt', 'Khá', 'Đạt']

        df['status'] = np.select(conditions, choices, default='Chưa đạt')
        avg_dict = df.set_index('student_id')[['score', 'status']].to_dict('index')
   
        for student in data['students']:
            student_id = student['student_id']
            academic_result = avg_dict.get(student_id)
            student_period_sum = self.academic_student_repo.get_student_period_summary({'student_id': student['student_id'],
                                                                                        'period_id': data['period_id']})

            student_period_sum.score = academic_result['score']
            student_period_sum.note = student['note']
            student_period_sum.conduct = student['conduct']
            student_period_sum.absent_day = student['absent_day'] if student['absent_day'] else 0
            student_period_sum.status = academic_result['status']
 
    def ranking_for_summary(self, lesson_scores: list):
        max_lesson = lesson_scores.shape[1]
        min_required_lesson = max_lesson - 1

        cond_good = ((np.all(lesson_scores >= 6.5, axis=1)) & (np.sum(lesson_scores >= 8, axis=1) >= 6))

        cond_fair_A = ((np.all(lesson_scores >= 5, axis=1)) & (np.sum(lesson_scores >= 6.5, axis=1) >= 6))
        cond_fair_B = ((np.sum(lesson_scores >= 6.5, axis=1) == min_required_lesson) & (np.sum(lesson_scores >= 8, axis=1) >= 6) & (np.sum(lesson_scores < 6.5, axis=1) == 1))
        cond_fair = cond_fair_A | cond_fair_B

        cond_avg_A = ((np.all(lesson_scores >= 3.5, axis=1)) & (np.sum(lesson_scores >= 5, axis=1) >= 6))
        cond_avg_B = ((np.sum(lesson_scores >= 6.5, axis=1) == min_required_lesson) & (np.sum(lesson_scores >= 8, axis=1) >= 6) & (np.sum(lesson_scores < 5, axis=1) == 1))
        cond_avg_C = ((np.sum(lesson_scores >= 5, axis=1) == min_required_lesson) & (np.sum(lesson_scores >= 6.5, axis=1) >= 6) & (np.sum(lesson_scores < 5, axis=1) == 1))
        cond_avg = cond_avg_A | cond_avg_B | cond_avg_C

        return cond_good, cond_fair, cond_avg
    
    def handle_show_student_for_year_summary(self, data):
        lessons_score = self.academic_student_repo.get_year_lesson_total_by_student_for_class(data)
        if lessons_score:
            lessons_score_df = pd.DataFrame(lessons_score, columns=['student_id', 'lessons'])
        
        lessons_score = self.academic_student_repo.get_temp_year_lesson_total_by_student_for_class(data)
        lessons_score_df = pd.DataFrame(lessons_score, columns=['student_id', 'lessons'])
        
        info = self.academic_student_repo.get_student_year_summary_infos(data)
        info_df = pd.DataFrame(info, columns = ['student_id', 'name', 'score', 'status', 'conduct', 'absent_day', 'note']).replace({np.nan: None})

        #merge info va chuyen ve nested dict
        output = lessons_score_df.merge(info_df, on = 'student_id', how = 'left').replace({np.nan: None}).to_dict(orient = 'records')                                  
        return output

    def handle_record_academic_year_result(self, data):
        lesson_totals = self.academic_student_repo.get_avg_annual_by_class_year(data)

        df = pd.DataFrame(lesson_totals, columns=['student_id', 'scores'])

        if df['scores'].apply(lambda x: any(v is None for v in x)).any():
            raise CustomException('Còn học sinh chưa được tổng kết!')

        score_matrix = np.array(df['scores'].to_list(), dtype=float)
        conditions = self.ranking_for_summary(score_matrix)
        choices = ['Tốt', 'Khá', 'Đạt']

        df['learning_status'] = np.select(conditions, choices, default='Chưa đạt')
        df['score'] = np.round(score_matrix.mean(axis=1), 2)
        avg_status = df.set_index(['student_id'])[['learning_status', 'score']].to_dict(orient='index')

        for student in data['students']:
            student_id = student['student_id']
            academic_result = avg_status.get(student_id)
            student_year_summary = self.academic_student_repo.get_student_year_summary({'student_id': student_id,
                                                                                        'year_id': data['year_id']})
            
            if academic_result['learning_status'] == 'Chưa đạt':
                self.add_to_retest(student_id, data['year_id'])
                student_year_summary.status = 'Thi lại'
                student_year_summary.retest_status = True

            elif academic_result['learning_status'] != 'Chưa đạt' and student_year_summary.grade == 12:
                student_year_summary.status = 'Hoàn thành'

            elif academic_result['learning_status'] != 'Chưa đạt' and student_year_summary.grade < 12:
                student_year_summary.status = 'Lên lớp'
                student_year_summary.review_status = True

            student_year_summary.score = academic_result['score']
            student_year_summary.learning_status = academic_result['learning_status']
            student_year_summary.conduct = student['conduct']
            student_year_summary.absent_day = student['absent_day'] if student['absent_day'] else 0
            student_year_summary.note = student['note']

    def add_to_retest(self, student_id, year_id):
        #tu stu, year lay less co diem chua dat
        self.academic_student_repo.insert_student_lesson_year_for_retest(student_id, year_id)

    def handle_show_students_for_retest(self, data):
        result = self.academic_student_repo.get_students_for_retest(data)
        keys = ['student_id', 'name', 'class_room', 'lesson_score', 'note']
        return [dict(zip(keys, values)) for values in result]
    
    def handle_add_score_to_retest_for_student(self, data, year_id, user_id):

        detail_changes = []
        for student in data:
            stu = self.student_service.handle_get_student_by_id(student)
            detail_changes.append(stu.name)
            for lesson_id, score in student['lessons'].items():
                self.academic_student_repo.update_retest_for_score({'student_id': student['student_id'],
                                                                    'year_id': year_id,
                                                                    'lesson_id': lesson_id,
                                                                    'score': score['score']})
        
        self.activity_log_service.handle_record_activity_log({'user_id': user_id,
                                                              'module': 'entity',
                                                              'target_id': [i.get('student_id') for i in data],
                                                              'action': 'UPDATE',
                                                              'detail': f'Thêm điểm thi lại: {', '.join(detail_changes)}'})
        self.db.session.commit()

    def handle_summary_retest_by_year(self, year_id):
        #check đã đủ điểm chưa
        #tiến hành summary
        is_full_score = self.academic_student_repo.check_retest_score_by_year(year_id)
        if not all(is_full_score):
            raise CustomException('Vẫn còn chưa nhập đủ điểm cho học sinh!')
        
        retest_score_students = self.academic_student_repo.get_retest_score_by_year(year_id)
        retest_df = pd.DataFrame(retest_score_students, columns=['student_id', 'retest'])
        passed_score_students = self.academic_student_repo.get_passed_score_by_year(year_id)
        passed_df = pd.DataFrame(passed_score_students, columns=['student_id', 'passed'])

        df = retest_df.merge(passed_df, on='student_id', how='left')
        df['merge'] = df.apply(lambda x: x['retest'] + x['passed'], axis=1)

        score_matrix = np.array(df['merge'].to_list(), dtype=float)
        conditions = self.ranking_for_summary(score_matrix)
        choices = ['Tốt', 'Khá', 'Đạt']
        df['rank'] = np.select(conditions, choices, default='Chưa đạt')

        students = df[['student_id','rank']].to_dict('records')
        for student in students:
            student_year_summary = self.get_student_year_summary({'student_id': student['student_id'],
                                                                  'year_id': year_id})
            if student['rank'] != 'Chưa đạt':
                if student_year_summary.grade == 12:
                    student_year_summary.status = 'Hoàn thành'

                else:
                    student_year_summary.status = 'Lên lớp'
                    student_year_summary.retest_status = True
                    student_year_summary.review_status = True

            else:
                student_year_summary.status = 'Lưu ban'
                student_year_summary.retest_status = True
                student_year_summary.review_status = True

        self.db.session.commit()
            
############## tinh điểm cho từng môn học để tổng kết năm học
    def handle_record_lesson_result_by_year(self, data):
        lesson_avgs = self.academic_student_repo.calc_lesson_total_by_class_year_for_student(data)
        self.academic_student_repo.upsert_student_lesson_annual(lesson_avgs)

    def handle_review_students(self, data):
        #summary current year by student
        student_year_summary = self.get_student_year_summary(data)
        student_year_summary.status = data['status']
        student_year_summary.review_status = True

        #insert new year summary
        if data['status'] == 'Lên lớp':
            grade = student_year_summary.grade + 1          
        else: 
            grade = student_year_summary.grade

        self.academic_student_repo.upsert_student_year_summary({'student_id': data['student_id'],
                                                                'year_id': data['next_year_id'],
                                                                'grade': grade,
                                                                'is_new_student': True})

    def handle_transfer_class_for_students(self, data):
        #update cho year_summary
        self.academic_student_repo.update_class_room_for_year_summary_by_student_year(data)
        #update cho period_summary
        self.academic_student_repo.update_class_room_for_period_summary_by_student_period(data)

    def get_student_period_summary(self, data):
        student_period_summary = self.academic_student_repo.get_student_period_summary(data)
        if not student_period_summary:
            raise NotFound_Exception('Không tìm thấy student period summary!')
        
        return student_period_summary

    def handle_update_student_assign_status(self, data):
        data['year_id'] = self.academic_get_service.handle_get_prev_year_id(data)
    
        student_year_summary = self.get_student_year_summary(data)
        student_year_summary.assign_status = True

    def handle_get_student_lesson_period(self, data):
        student_lesson_period = self.academic_student_repo.get_student_lesson_period(data)
        if not student_lesson_period:
            raise NotFound_Exception('Không tìm thấy student_lesson_period!')
        
        return student_lesson_period

    def handle_show_students_for_class_assignment(self, data: dict): # for assign student to class
        #get prev year id
        data['prev_year_id'] = self.academic_get_service.handle_get_prev_year_id(data)

        result = self.academic_student_repo.show_students_for_class_assignment(data)
        keys = ['student_id', 'student_code', 'name', 'score', 'conduct', 'learning_status', 'class_room', 'note', 'status', 'assign_class','class_room_id']
        return [dict(zip(keys, values)) for values in result]

    def handle_show_students_for_approval(self, data):
        result = self.academic_student_repo.show_students_for_approval(data)
        keys = ['student_id', 'student_code', 'name', 'score', 'conduct', 'learning_status', 'absent_day', 'class_room_id', 'note', 'status', 'review_status']
        return [dict(zip(keys, values)) for values in result]
    
    def handle_show_class_room_for_student(self, data):
        result = self.academic_student_repo.show_class_room_by_student_period(data)
        keys = ['class_room_id', 'class_room', 'grade']
        return [dict(zip(keys, values)) for values in result]
    
    def handle_show_weak_students(self, data):
        students = self.academic_student_repo.get_weak_students(data)
        keys = ['name', 'class_room', 'scores']
        return [dict(zip(keys, values)) for values in students]
    
    def handle_show_summary_result_for_class(self, data):
        students = self.academic_student_repo.get_student_summary_results_for_class(data)
        students_keys = ['name', 'student_code', 'score', 'conduct', 'learning_status', 'status', 'note']

        students_output = [dict(zip(students_keys, values)) for values in students]
        summary_result = self.academic_student_repo.get_summary_result_for_class(data)

        result = {'summary': summary_result, 'students': students_output}
  
        return result
    
    def handle_update_summary_by_score_for_student(self, data):
        student_lesson_period = self.handle_get_student_lesson_period({'period_id': data['period_id'],
                                                                       'student_id': data['student_id'],
                                                                       'lesson_id': data['lesson_id']})
        if student_lesson_period:
            self.reset_slp(student_lesson_period)

            student_period_summary = self.get_student_period_summary({'period_id': data['period_id'],
                                                                      'student_id': data['student_id']})
            if student_period_summary != None:
                self.reset_sps(student_period_summary)

                student_lesson_annual = self.academic_student_repo.get_student_lesson_annual({'year_id': data['year_id'],
                                                                                            'student_id': data['student_id'],
                                                                                            'lesson_id': data['lesson_id']})
                if student_lesson_annual != None:
                    self.reset_sla(student_lesson_annual)

                    student_year_summary = self.get_student_year_summary({'year_id': data['year_id'],
                                                                          'student_id': data['student_id']})
                    if student_year_summary.learning_status != None:
                        self.reset_sym(student_year_summary)

    def reset_slp(self, slp):
        slp.status = None
        slp.total = None
    
    def reset_sps(self, sps):
        sps.status = None
        sps.score = None
        sps.conduct = None
        sps.absent_day = 0

    def reset_sla(self, sla):
        sla.status = None
        sla.avg_annual = None

    def reset_sym(self, sym):
        sym.learning_status = None
        sym.score = None
        sym.conduct = None
        sym.absent_day = 0
        sym.status = None
        sym.review_status = None
        sym.retest_status = None

class Academic_Score_Service:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.academic_score_repo = self.repo.score
        self.academic_get_service = AcademicGetService(db, repo)
        self.academic_validation = Academic_Validation(db, repo)
        self.academic_student_service = Academic_Student_Service(db, repo)
    
    def handle_get_score_for_student(self, student_lesson_period_id, score_type_id, attempt):
        score = self.academic_score_repo.get_score_for_student(student_lesson_period_id, score_type_id, attempt)
        return score
    
    def init_meta_score_frame(self):
        meta_score = self.academic_score_repo.init_score_frame()
        meta_score_series = [[str(score_type_id), str(attempt)] for score_type_id, max_c in meta_score for attempt in range(1, max_c + 1)]
        meta_score_df = pd.DataFrame(meta_score_series, columns = ['score_type_id', 'attempt'])
        return meta_score_df
    
###### show điểm tất cả môn cho học sinh    
    def score_frame_for_student_by_period(self, data):
        meta_score_df = self.init_meta_score_frame()

        lessons = self.academic_score_repo.get_lessons_by_student_id(data)
        lessons_df = pd.DataFrame(lessons, columns=['student_id', 'lesson_id'])

        lesson_meta_score_df = meta_score_df.assign(key=1).merge(lessons_df.assign(key=1), on=['key'], how='left').drop(['key', 'student_id'], axis=1)
        
        result = self.academic_score_repo.get_lessons_scores_by_student_period(data)        
        df = pd.DataFrame(result, columns=['lesson_id', 'score_type_id', 'attempt', 'score'])
        final_df = lesson_meta_score_df.merge(df, on = ['lesson_id', 'score_type_id', 'attempt'], how = 'left')
        final_df = final_df.replace({np.nan: None})

        score_flat = final_df.set_index(['lesson_id', 'score_type_id', 'attempt'])['score'].to_dict()
        score_dict = defaultdict(lambda: defaultdict(dict))

        for (lesson_id, score_type_id, attempt), score in score_flat.items():
            score_dict[lesson_id][score_type_id][attempt] = score

        score_df = pd.Series(dict(score_dict)).rename('scores').rename_axis('lesson_id').reset_index()
        return score_df

    def handle_show_scores_by_student_and_period(self, data):
        score_df = self.score_frame_for_student_by_period(data)
        info = self.academic_score_repo.get_lessons_summary_by_student_period(data)

        info_df = pd.DataFrame(info, columns=['lesson_id', 'lesson', 'total', 'status', 'note'])
        result = score_df.merge(info_df, on = 'lesson_id', how = 'left')
        result = result.replace({np.nan: None})

        return result.to_dict(orient = 'records')
    
########## cho điểm học sinh theo môn học    
    def score_frame_for_lesson_class(self, data):
        meta_score_df = self.init_meta_score_frame()
        
        result = self.academic_score_repo.get_score_by_student_lesson_period(data)
        result_df = pd.DataFrame(result, columns=['student_id', 'score_type_id', 'attempt', 'score'])

        # lấy student_id duy nhất
        df_students = result_df[['student_id']].drop_duplicates()

        # cross join students × score_frame
        df_cross = df_students.assign(key=1).merge(meta_score_df.assign(key=1), on='key').drop('key', axis=1)

        # merge thêm score  
        score_df = df_cross.merge(result_df[['student_id','score_type_id','attempt','score']],
                                  on=['student_id','score_type_id','attempt'],
                                  how='left')
        
        score_df = score_df.replace({np.nan: None}) 

        score = score_df.set_index(['student_id', 'score_type_id', 'attempt'])['score'].to_dict()
        
        flat_score = defaultdict(lambda: defaultdict(dict))
        for (student_id, score_type_id, attempt), scores in score.items():
            flat_score[student_id][score_type_id][attempt] = scores
        
        score_df = pd.Series(dict(flat_score)).rename('scores').rename_axis('student_id').reset_index().sort_values(['student_id'])
        return score_df

    def handle_upsert_score(self, data):
        scores = []
        for score_type_id, score in data['scores'].items():
            for attempt in score.keys():
                score_check = self.academic_score_repo.get_score(data['student_lesson_period_id'], score_type_id, attempt)
                if score_check:
                    self.academic_student_service.handle_update_summary_by_score_for_student({'student_id': data['student_id'],
                                                                                              'period_id': data['period_id'],
                                                                                              'year_id': data['year_id'],
                                                                                               'lesson_id': data['lesson_id']})
                    
                self.academic_score_repo.upsert_score({'student_lesson_period_id': data['student_lesson_period_id'],
                                                       'score_type_id': score_type_id,
                                                       'attempt': attempt,
                                                       'score': score[attempt]})

                scores.append(score[attempt])
        return scores

    
    def handle_show_scores_by_lesson_class(self, data):
        info = self.academic_score_repo.get_summary_result_for_student_lesson_period(data)
        info_df = pd.DataFrame(info, columns=['student_id', 'name', 'total', 'status', 'note'])

        if info_df['status'].isna().any():
            temp_info = self.academic_score_repo.get_temp_summary_result_for_student_lesson_period(data)
            temp_info_df = pd.DataFrame(temp_info, columns=['student_id', 'total']) 
            info_df = info_df.drop(columns='total').merge(temp_info_df, on=['student_id'], how='left')
                       
        # lấy thông tin thêm và merge
        score_df = self.score_frame_for_lesson_class(data)
 
        final_df = score_df.merge(info_df, on = ['student_id'], how = 'left').replace({np.nan: None})
        output = final_df.to_dict(orient='records')
        return output
    
############## tinh điểm cho từng môn học để tổng kết học kỳ
    def get_avg_scores_for_students_by_lesson_class_and_period(self, data):
        result = self.academic_score_repo.get_avg_scores_for_students_by_lesson_class_and_period(data)
        result_df = pd.DataFrame(result, columns=['student_id', 'total', 'status'])
        result_dict = result_df.to_dict(orient='records')

        return result_dict
    
    def check_exam(self, data):
        exam = self.academic_score_repo.get_exam_score(data)
        if exam is None:
            raise NotFound_Exception('Học sinh vẫn chưa có điểm kiểm tra giữa kỳ!')
    
    def check_final_exam(self, data):
        final_exam = self.academic_score_repo.get_final_exam_score(data)
        if final_exam is None:
            raise NotFound_Exception('Học sinh vẫn chưa có điểm thi cuối kỳ!')

class Academic_Schedule_Service:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.schedule_repo = self.repo.schedule
        self.academic_get_service = AcademicGetService(db, repo)

    def handle_get_teacher_id_by_lesson_and_class_room(self, data):
        teacher_id = self.schedule_repo.get_teacher_id_by_lesson_and_class_room(data)
        if teacher_id:
            return teacher_id        
       
    def init_schedule_frame(self):
        lesson_times = list(range(1, 6))
        days = list(range(1,7))

        frame_df = pd.MultiIndex.from_product([lesson_times, days], names=['period', 'day']).to_frame(index=False)
        return frame_df
    
    def handle_show_schedules_in_tool(self, data):
        frame_df = self.init_schedule_frame()
        schedule = self.schedule_repo.get_schedule_for_class(data)
        schedule_df = pd.DataFrame(schedule, columns=['period', 'day', 'lesson_id', 'lesson'])

        final_df = frame_df.merge(schedule_df, on = ['period', 'day'], how = 'left').replace({np.nan: None})
        final = final_df.set_index(['period', 'day'])[['lesson_id', 'lesson']].to_dict(orient='index')
        output = defaultdict(dict)

        for (period, day), lesson in final.items():
            output[period][day] = lesson

        return output
    
    def init_schedule_frame_for_admin(self, data):
        period = list(range(1,6))
        class_rooms = self.academic_get_service.handle_get_class_rooms_by_year(data)
        frame_df = pd.MultiIndex.from_product([period, class_rooms], names=['period', 'class_room']).to_frame(index=False)
        return frame_df
    
    def handle_show_today_schedules(self, data):
        schedule = self.schedule_repo.get_schedule_for_admin(data)
        schedule_df = pd.DataFrame(schedule, columns=['period', 'class_room', 'lesson', 'teacher'])

        frame_df = self.init_schedule_frame_for_admin(data)
        final_df = frame_df.merge(schedule_df, on=['period', 'class_room'], how='left').replace({np.nan: None})
        final = final_df.set_index(['period', 'class_room'])[['lesson', 'teacher']].to_dict(orient='index')

        output = defaultdict(lambda: defaultdict(dict))
        for (period, class_room), lesson in final.items():
            output[period][class_room] = lesson
        
        return output

    def handle_show_schedules(self, data):
        frame_df = self.init_schedule_frame()

        if data['role'] == 'Student':
            schedule = self.schedule_repo.get_schedule_for_class(data)
            schedule_df = pd.DataFrame(schedule, columns = ['period', 'day', 'lesson_id', 'lesson'])

            final_df = frame_df.merge(schedule_df, on = ['period', 'day'], how = 'left')
            final_df = final_df.replace({np.nan: None})
            
            output = defaultdict(dict)
            result = (final_df.set_index(['period', 'day'])[['lesson_id', 'lesson']].to_dict(orient='index'))
            for (period, day), lesson in result.items():
                output[str(period)][str(day)] = lesson
            
        else:
            schedule = self.schedule_repo.get_schedule_for_teacher(data)
            schedule_df = pd.DataFrame(schedule, columns=['period', 'day', 'class_room_id', 'class_room'])

            final_df = frame_df.merge(schedule_df, on = ['period', 'day'], how = 'left')
            final_df = final_df.replace({np.nan: None})
            
            output = defaultdict(dict)
            result = (final_df.set_index(['period', 'day'])[['class_room_id', 'class_room']].to_dict(orient='index'))
            for (period, day), class_room in result.items():
                output[str(period)][str(day)] = class_room
  
        return output

    def handle_upsert_schedule(self, data):
        #period id, class id, lesson id, day of week, lesson time, teacher id
        period_id = self.academic_get_service.handle_get_period_id(data)
        schedules = []
        for lesson_time, day_lesson in data['schedules'].items():
            for day, lessons in day_lesson.items():
                lesson_id = lessons.get('lesson_id')
                schedules.append({"lesson_time": lesson_time,
                                  "day_of_week": day,
                                  "lesson_id": lesson_id})
        
        for schedule in schedules:
            if schedule.get('lesson_id') == None:
                self.schedule_repo.delete_schedule({'lesson_time': schedule['lesson_time'],
                                                    'day_of_week': schedule['day_of_week'],
                                                    'period_id': period_id,
                                                    'class_room_id': data['class_room_id']})
            else:
                try:
                    self.schedule_repo.bulk_upsert_schedule({'lesson_time': schedule['lesson_time'],
                                                             'day_of_week': schedule['day_of_week'],
                                                             'lesson_id': schedule['lesson_id'],
                                                             'period_id': period_id,
                                                             'class_room_id': data['class_room_id'],
                                                             'year_id': data['year_id']})
                except:
                    self.db.session.rollback()
                    lesson = self.academic_get_service.handle_get_lesson_by_id({'lesson_id': schedule['lesson_id']})
                    raise DuplicateException(f"môn {lesson.lesson} tiết {schedule['lesson_time']} thứ {int(schedule['day_of_week']) + 1} bị trùng giờ dạy!")
    
        self.db.session.commit()

    def handle_remove_teacher_from_schedules(self, data):
        self.schedule_repo.remove_teacher_from_schedule_by_teacher_period_lesson(data)

### Attendence    
    def handle_show_schedules_for_attendence(self, data):
        result = self.schedule_repo.get_schedules_by_teacher_and_day(data)
        keys = ['class_room_id', 'class_room', 'day']
        return [dict(zip(keys, values)) for values in result]

    def handle_show_lesson_times_for_class_by_day(self, data):
        lesson_day = list(range(1,7))
        monday_this_week = data['day'] - timedelta(days=data['day'].weekday())
        dates = [monday_this_week + timedelta(days=d - 1) for d in lesson_day]
        data['dates'] = dates
        week_df = pd.DataFrame(dates, columns=['dates'])
 
        attendence = self.schedule_repo.get_student_for_attendence_by_class_period(data)
        attendence_df = pd.DataFrame(attendence, columns=['student_id', 'name', 'dates', 'status', 'note'])

        students_df = attendence_df[['student_id', 'name', 'note']].drop_duplicates()
        
        week_df = week_df.merge(students_df, how='cross')
        df = week_df.merge(attendence_df, on=['student_id', 'name', 'dates', 'note'], how='left').replace({np.nan: None})
        output = []

        for (student_id, name), g in df.groupby(['student_id', 'name']):
            note = g['note'].dropna().iloc[0] if g['note'].notna().any() else None
            g = g.sort_values('dates')
            output.append({
                'student_id': int(student_id), 
                'name': name, 
                'note': note,
                'dates': dict(zip(g['dates'].astype(str), g['status']))
            })

        return output
    
    def handle_make_attendence(self, data):
        period_id = self.academic_get_service.handle_get_period_id(data)
        for student in data['students']:
            self.schedule_repo.upsert_attendence({'student_id': student['student_id'],
                                                  'status': student['status'],
                                                  'note': student['note'],
                                                  'date': data['day'],
                                                  'period_id': period_id})
        
        self.db.session.commit()

                

      


    