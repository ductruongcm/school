from ..validation import Academic_Teacher_Validation, Academic_Validation
from collections import defaultdict
from .core import AcademicGetService
from app.utils import filter_fields
from app.exceptions import NotFound_Exception, CustomException
from datetime import date
import pandas as pd
import numpy as np

class Academic_Teacher_Service:
    def __init__(self, db, repo):
        self.repo = repo(db)
        self.academic_teacher_repo = self.repo.academic_teacher
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
            self.academic_teacher_validation.check_existing_teacher_in_teaching_classes({'teaching_class_ids': to_add,
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
                period_id = self.academic_get_service.handle_get_period_id({'year_id': year_id,'semester_id': semester_id})
                self.record_academic_results_for_semester(student_id, data['lesson_id'], period_id, data[f'score_{semester_id}'])

    def handle_record_prev_year_academic_semester_result(self, data):
        for semester_id in [1,2]:
            period_id = self.academic_get_service.handle_get_period_id({'year_id': data['year_id'],'semester_id': semester_id})
            lesson_totals = self.academic_student_repo.get_semester_lesson_totals_by_student_and_period({'student_id': data['student_id'],
                                                                                                        'period_id': period_id})
            status , score = self.rank_academic_result(lesson_totals)
            self.handle_add_student_period_summary({'student_id': data['student_id'],
                                                    'period_id': period_id,
                                                    'grade': data['grade'],
                                                    'status': status,
                                                    'score': score})

    def record_academic_results_for_semester(self, student_id, lesson_id, period_id, total):
        status = 'Đạt' if total >=5 else 'Không đạt'
        self.academic_student_repo.insert_student_lesson_period({'student_id': student_id,
                                                                 'lesson_id': lesson_id,
                                                                 'period_id': period_id,
                                                                 'total': total,
                                                                 'status': status})  

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

        student_year_summary = self.academic_student_repo.get_student_year_summary(data)
        student_year_summary.score = score
        student_year_summary.learning_status = learning_status
        student_year_summary.conduct = data['conduct']
        student_year_summary.absent_day = data['absent_day']
        student_year_summary.note = data['note']

    def handle_record_academic_semester_results(self, data):
        #get less result add stu per sum 
        lesson_totals = self.academic_student_repo.get_semester_lesson_totals_by_student_and_period(data)
        learning_status, score = self.rank_academic_result(lesson_totals)

        student_period_summary = self.get_student_period_summary(data)
        student_period_summary.score = score
        student_period_summary.status = learning_status
        student_period_summary.conduct = data['conduct']
        student_period_summary.absent_day = data['absent_day']
        student_period_summary.note = data['note']
    
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
                                                                'grade': grade})

    def handle_transfer_class_for_students(self, data):
        #get stu year sum
        student_year_summary = self.get_student_year_summary(data)
        student_year_summary.class_room_id = data['class_room_id']

        #get stu per sum
        period_ids = self.academic_get_service.handle_get_period_ids_by_year(data)
        for period_id in period_ids:
            student_period_summary = self.get_student_period_summary({'student_id': data['student_id'],
                                                                      'period_id': period_id})
            student_period_summary.class_room_id = data['class_room_id']

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
    
    def init_lessons_frame_for_class(self, data):
        student_lesson_frame = self.academic_student_repo.get_lessons_and_students_for_summary(data)
        student_lesson_df = pd.DataFrame(student_lesson_frame, columns=['student_id', 'lesson_id', 'lesson'])
        return student_lesson_df
    
    def convert_raw_data_to_final_dict(self, data, student_lesson_total):
        student_lesson_df = self.init_lessons_frame_for_class(data)
        student_lesson_total_df = pd.DataFrame(student_lesson_total, columns=['student_id', 'lesson_id', 'lesson', 'total'])
    
        raw_df = student_lesson_df.merge(student_lesson_total_df, on = ['student_id', 'lesson_id', 'lesson'], how = 'left')
        raw_df = raw_df.replace({np.nan: None})

        raw_dict = raw_df.set_index(['student_id', 'lesson_id', 'lesson'])['total'].to_dict()
        final_dict = defaultdict(lambda: defaultdict(dict))

        for (student_id, lesson_id, lesson), total in raw_dict.items():
            final_dict[student_id][lesson_id][lesson] = total
        
        final_df = pd.Series(dict(final_dict)).rename('lessons').rename_axis('student_id').reset_index()
        return final_df
        
    def handle_show_student_for_semester_summary(self, data):
        student_lesson_total = self.academic_student_repo.get_semester_lesson_total_by_student_for_class(data)

        final_df = self.convert_raw_data_to_final_dict(data, student_lesson_total)
        info = self.academic_student_repo.get_student_semester_summary_infos(data)
        info_df = pd.DataFrame(info, columns = ['student_id', 'name','score', 'learning_status', 'conduct', 'absent_day', 'note'])

        output = final_df.merge(info_df, on = 'student_id', how = 'left').to_dict(orient = 'records')

        return output
    
    def handle_show_student_for_year_summary(self, data):
        student_lesson_total = self.academic_student_repo.get_year_lesson_total_by_student_for_class(data)

        final_df = self.convert_raw_data_to_final_dict(data, student_lesson_total)

        #info them
        info = self.academic_student_repo.get_student_year_summary_infos(data)
        info_df = pd.DataFrame(info, columns = ['student_id', 'name','score', 'learning_status', 'conduct', 'absent_day', 'note'])

        #merge info va chuyen ve nested dict
        output = final_df.merge(info_df, on = 'student_id', how = 'left').to_dict(orient = 'records')                                  
  
        return output

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

class Academic_Score_Service:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.academic_score_repo = self.repo.score
        self.academic_get_service = AcademicGetService(db, repo)
        self.academic_validation = Academic_Validation(db, repo)

    def handle_upsert_score(self, data):
        print(data)
        scores = []
        for score_type_id, score in data['scores'].items():
            for attempt in score.keys():
                self.academic_score_repo.upsert_score({'student_lesson_period_id': data['student_lesson_period_id'],
                                                       'score_type_id': score_type_id,
                                                       'attempt': attempt,
                                                       'score': score[attempt]})

                scores.append(score[attempt])
        return scores
    
    def handle_show_scores_by_student_and_period(self, data):
        score_df = self.score_frame_for_student_by_period(data)
        info = self.academic_score_repo.get_lessons_summary_by_student_period(data)

        info_df = pd.DataFrame(info, columns=['lesson_id', 'lesson', 'total', 'status', 'note'])
        result = score_df.merge(info_df, on = 'lesson_id', how = 'left')
        result = result.replace({np.nan: None})

        return result.to_dict(orient = 'records')
    
    def init_meta_score_frame(self):
        meta_score = self.academic_score_repo.init_score_frame()
        meta_score_series = [[str(score_type_id), str(attempt)] for score_type_id, max_c in meta_score for attempt in range(1, max_c + 1)]
        meta_score_df = pd.DataFrame(meta_score_series, columns = ['score_type_id', 'attempt'])
        return meta_score_df

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

        score_df = score_df.set_index(['student_id', 'score_type_id', 'attempt'])['score'].to_dict()

        flat_score_df = defaultdict(lambda: defaultdict(dict))
        for (student_id, score_type_id, attempt), score in score_df.items():
            flat_score_df[student_id][score_type_id][attempt] = score
        
        score_df = pd.Series(dict(flat_score_df)).rename('scores').rename_axis('student_id').reset_index().sort_values(['student_id'])

        return score_df
    
    def handle_show_scores_by_lesson_class(self, data):
        info = self.academic_score_repo.get_student_lesson_period_info(data)
        print(info)
        info_df = pd.DataFrame(info, columns=['student_id', 'name', 'total', 'status', 'note'])
        score_df = self.score_frame_for_lesson_class(data)
        # lấy thông tin thêm và merge

        final_df = score_df.merge(info_df, on = ['student_id'], how = 'left')
        output = final_df.to_dict(orient='records')
        
        return output
    
    def get_avg_scores_for_students_by_lesson_class_and_period(self, data):
        result = self.academic_score_repo.get_avg_scores_for_students_by_lesson_class_and_period(data)
        result_df = pd.DataFrame(result, columns=['student_id', 'total'])

        conditions = [result_df['total'] >= 8,
                      result_df['total'] >= 6.5,
                      result_df['total'] >= 5,
                      result_df['total'] < 5]
        
        choices = ['Giỏi', 'Khá', 'Trung bình', 'Không đạt']

        result_df['status'] = np.select(conditions, choices, default='Chưa đánh giá')
        result_dict = result_df.to_dict(orient='records')

        return result_dict
    
    def check_exam(self, data):
        exam = self.academic_score_repo.get_exam_score(data)
        if not exam:
            raise NotFound_Exception('Học sinh vẫn chưa có điểm kiểm tra giữa kỳ!')
    
    def check_final_exam(self, data):
        final_exam = self.academic_score_repo.get_final_exam_score(data)
        if not final_exam:
            raise NotFound_Exception('Học sinh vẫn chưa có điểm thi cuối kỳ!')
        
    def handle_show_weak_students(self, data):
        students = self.academic_score_repo.get_weak_students(data)
        keys = ['name', 'class_room', 'scores']
        return [dict(zip(keys, values)) for values in students]

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
    
    def handle_get_schedule_id(self, data):
        schedule_id = self.schedule_repo.get_schedule_id(data)
        if schedule_id:
            return schedule_id
   
    def handle_show_schedules(self, data):
        frame_df = self.init_schedule_frame()

        if data['role'] == 'Teacher':
            schedule = self.schedule_repo.get_schedule_for_teacher(data)
            schedule_df = pd.DataFrame(schedule, columns=['period', 'day', 'class_room_id', 'class_room'])
            final_df = frame_df.merge(schedule_df, on = ['period', 'day'], how = 'left')
            final_df = final_df.replace({np.nan: None})
            
            output = defaultdict(dict)
            result = (final_df.set_index(['period', 'day'])[['class_room_id', 'class_room']].to_dict(orient='index'))
            for (period, day), class_room in result.items():
                output[str(period)][str(day)] = class_room

        elif data['role'] == 'admin':
            schedule = self.schedule_repo.get_schedule_for_admin(data)

            output = defaultdict(lambda: defaultdict(dict))
            for (period, class_room, lesson, teacher) in schedule:
                output[period][class_room][lesson] = teacher

        else:
            schedule = self.schedule_repo.get_schedule_for_class(data)
            schedule_df = pd.DataFrame(schedule, columns = ['period', 'day', 'lesson_id', 'lesson'])

            final_df = frame_df.merge(schedule_df, on = ['period', 'day'], how = 'left')
            final_df = final_df.replace({np.nan: None})
            
            output = defaultdict(dict)
            result = (final_df.set_index(['period', 'day'])[['lesson_id', 'lesson']].to_dict(orient='index'))
            for (period, day), lesson in result.items():
                output[str(period)][str(day)] = lesson
        
        return dict(output)
    
    def init_schedule_frame(self):
        lesson_times = list(range(1, 6))
        days = list(range(1,7))

        frame_df = pd.MultiIndex.from_product([lesson_times, days], names=['period', 'day']).to_frame(index=False)
        return frame_df

    def handle_upsert_schedule(self, data):
        period_id = self.academic_get_service.handle_get_period_id(data)
        for lesson_time, day_lesson in data['schedules'].items():
            for day, values in day_lesson.items():
                for lesson_id in values.values():
                    teacher_id = self.handle_get_teacher_id_by_lesson_and_class_room({'class_room_id': data['class_room_id'],
                                                                                      'lesson_id': lesson_id,
                                                                                      'year_id': data['year_id']})
                    insert_data = {'lesson_time': lesson_time,
                                   'day_of_week': day,
                                   'period_id': period_id,
                                   'class_room_id': data['class_room_id'],
                                   'teacher_id': teacher_id}
                    
                    if lesson_id is None:
                        #get schedule_id => delete schedule & teacher schedule by schedule id
                            self.schedule_repo.delete_schedule(insert_data)
                    
                    else:
                        insert_data.update({'lesson_id': lesson_id})
                        try:
                            self.schedule_repo.bulk_upsert_schedule(insert_data)
                        except:
                            raise CustomException('Bị trùng giờ dạy!')
        
        self.db.session.commit()
    
    def handle_show_schedules_by_teacher_day(self, data):
        result = self.schedule_repo.get_schedules_by_teacher_and_day(data)
        keys = ['class_room_id', 'class_room', 'lesson_time']
        return [dict(zip(keys, values)) for values in result]

    def handle_show_lesson_times_for_class_by_day(self, data):
        result = self.schedule_repo.get_lesson_time_by_class_day(data)
        if result:
            keys = ['name', 'student_id', 'lesson_time', 'note']
            return [dict(zip(keys, values)) for values in result]

    def handle_make_attendence(self, data):
        schedule_id = self.schedule_repo.get_schedule_id(data)
        if not schedule_id:
            raise NotFound_Exception('Không tìm thấy schedule id!')

        for student in data['students']:
            self.schedule_repo.upsert_attendence({'student_id': student['student_id'],
                                                  'status': student['status'],
                                                  'schedule_id': schedule_id,
                                                  'note': student['note']})
        
        self.db.session.commit()

                

      


    