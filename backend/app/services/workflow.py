from app.exceptions import DuplicateException
from .validation import Academic_Validation, User_Validation, Teacher_Validation, Academic_Teacher_Validation
from .student import StudentServices
from .teacher import TeacherService
from .log import ActivityLog_Service
from .academic.entity import Academic_Student_Service, Academic_Teacher_Service, Academic_Score_Service
from .academic.core import AcademicGetService
from .academic.relation import Academic_Relation_Service
from .user import UserService
from app.utils import filter_fields

class Student_Workflow:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.academic_validation = Academic_Validation(db, repo)
        self.student_service = StudentServices(db, repo)
        self.academic_get_service = AcademicGetService(db, repo)
        self.user_service = UserService(db, repo)
        self.academic_student_service = Academic_Student_Service(db, repo)
        self.activity_log_service = ActivityLog_Service(db, repo)
        self.academic_score_service = Academic_Score_Service(db, repo)

    def process_create_student(self, data, user_id):
        #check year, year_id, grade
        self.academic_validation.check_year(data)
        self.academic_validation.validate_year_id(data)
        self.academic_validation.validate_grade(data)

        data['class_room_id'] = None
        #add student
        student = self.student_service.handle_add_student(data)

        #generate student_code
        student_code = self.student_service.handle_generate_student_code(data)
        student.student_code = student_code

        #add user
        user_data = self.user_service.new_student_data_for_user(student_code)
        user = self.user_service.handle_add_user(user_data)

        #link user và student
        student.user_id = user.id
        data['student_id'] = student.id
        #add lich su hoc tap từng học kỳ
        self.academic_student_service.handle_record_prev_year_academic_semesters_results(data)
        
        #add lich su hoc tap ca năm
        self.academic_student_service.handle_record_prev_year_academic_year_result(data)

        self.activity_log_service.handle_record_activity_log({'user_id': user_id,
                                                              'module': 'student',
                                                              'action': 'CREATE',
                                                              'detail': f'Thêm học sinh {student.name} vào hệ thống'})
        self.db.session.commit()
        
        return data

    def process_review_students(self, data, year_id, user_id:int):
        detail_changes = []
        for item in data:
            item['year_id'] = self.academic_get_service.handle_get_prev_year_id({'year_id': year_id})

            student = self.student_service.handle_get_student_by_id(item)
            
            self.academic_student_service.handle_review_students(item)
            detail_changes.append(f'{student.name} - {item['status']}')
  
        self.activity_log_service.handle_record_activity_log({'user_id': user_id,
                                                              'module': 'user',
                                                              'target_id': [i.get('student_id') for i in data],
                                                              'action': 'APPROVE',
                                                              'detail': f'Xét duyệt học sinh: {', '.join(detail_changes)}'})
        self.db.session.commit()

    def process_assign_students_for_new_year(self, data, user_id):
        self.academic_validation.validate_year_id(data)
        self.academic_validation.validate_semester_id(data)
        period_ids = []
        for semester_id in [1, 2]:
            period_ids.append(self.academic_get_service.handle_get_period_id({'year_id': data['year_id'],
                                                                              'semester_id': semester_id}))
        detail_changes = []

        for item in data['student_assign_list']:
            self.academic_validation.validate_class_room_id(item)
            grade = self.academic_get_service.handle_get_grade_by_class_room(item)

            student = self.student_service.handle_get_student_by_id(item)

            #Bật True cho assign status 
            self.academic_student_service.handle_update_student_assign_status({'student_id': item['student_id'],
                                                                               'year_id': data['year_id']})
            
            #xếp lớp = insert new row in student_year_summary: student_id, year_id, grade, class_room_id
            self.academic_student_service.handle_add_student_year_summary({'student_id': item['student_id'],
                                                                           'year_id': data['year_id'],
                                                                           'grade': grade,
                                                                           'class_room_id': item['class_room_id']})
            
            #get lesson ids by grade
            lesson_ids = self.academic_get_service.handle_get_lesson_ids_by_grade_and_is_visible({'grade': grade})
            
            #insert new row in student period class_room_id
            for period_id in period_ids:
                self.academic_student_service.handle_add_student_period_summary({'student_id': item['student_id'],
                                                                                 'period_id': period_id,
                                                                                 'class_room_id': item['class_room_id']})

                #tạo liên kết học sinh và môn học của học kỳ 1: mỗi student_id + 1 period_id + all of lesson
                for lesson_id in lesson_ids:
                    self.academic_student_service.handle_add_student_lesson_period({'student_id': item['student_id'],
                                                                                    'period_id': period_id,
                                                                                    'lesson_id': lesson_id})
                    
                    self.academic_student_service.handle_add_student_year_summary

            detail_changes.append(f'{student.name}')

        self.activity_log_service.handle_record_activity_log({'user_id': user_id,
                                                              'module': 'student',
                                                              'target_id': [i.get('student_id') for i in data.get('student_assign_list')],
                                                              'action': 'ASSIGN TO CLASS',
                                                              'detail': f'Xếp lớp cho học sinh: {', '.join(detail_changes)}'})

        self.db.session.commit()

    def process_update_students(self, data, user_id):
        detail_change = []
        for item in data:
            student = self.student_service.handle_get_student_by_id(item)

            if 'name' in item:
                student.name = item['name']
                detail_change.append(f"Thay đổi tên {item['name']}")

            if any(keys in item for keys in ['gender', 'bod', 'tel', 'add', 'note']):
                student_info = self.student_service.handle_get_student_info_by_student({'student_id': student.id})
                item = filter_fields('gender', 'bod', 'tel', 'add', 'note', context=item)
                for key, value in item.items():
                    setattr(student_info, key, value)
                    detail_change.append(f"thay đổi thông tin {key}: {value}")

            if 'class_room_id' in item:
                student_year_summary = self.academic_student_service.get_student_year_summary(item)
                student_year_summary.class_room_id = item['class_room_id']
                detail_change.append(f"chuyển lớp {item['class_room_id']}")

        self.activity_log_service.handle_record_activity_log({'user_id': user_id,
                                                              'module': 'student',
                                                              'target_id': [i.get('student_id') for i in data],
                                                              'action': 'UPDATE',
                                                              'detail': detail_change})

        self.db.session.commit()

class Teacher_Workflow:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.user_validation = User_Validation(db, repo)
        self.teacher_validation = Teacher_Validation(db, repo)
        self.academic_teacher_validation = Academic_Teacher_Validation(db, repo)
        self.academic_validation = Academic_Validation(db, repo)
        self.academic_get_service = AcademicGetService(db, repo)
        self.user_service = UserService(db, repo)
        self.teacher_service = TeacherService(db, repo)
        self.academic_teacher_service = Academic_Teacher_Service(db, repo)
        self.activity_log_service = ActivityLog_Service(db, repo)
   
    def process_create_teacher(self, data):
        #check dup username, check lesson id, year id
        self.academic_validation.validate_lesson_id(data)
        self.academic_validation.validate_year_id(data)

        #add user
        user_data = self.user_service.new_teacher_data_for_user(data)
        user = self.user_service.handle_add_user(user_data)

        #create tmp_token, insert Tmp_token
        data['user_id'] = user.id
        token = self.user_service.handle_add_tmp_token(data)

        #add teacher
        teacher = self.teacher_service.handle_add_teacher(data)

        #check homeclass and add
        if data.get('class_room_id'):
            class_room = self.academic_get_service.handle_get_class_room_by_id(data)
            if class_room.teacher_id:
                raise DuplicateException('Lớp học đã có giáo viên chủ nhiệm!')
            class_room.teacher_id = teacher.id

        #check teach class and assign
        if data.get('teaching_class_ids'):
            self.academic_teacher_validation.check_existing_teacher_in_teaching_class(data)

            teaching_classes = self.academic_get_service.handle_get_teaching_class_by_class_rooms(data)
            for teach_class in teaching_classes:
                teach_class.teacher_id = data['teacher_id']   
        
        self.db.session.commit()

        #send password set mail
        data['token'] = token
        self.teacher_service.send_set_password_mail(data)

        return data
    
    def process_update_teacher(self, data):
        #check teacher_id, lesson_id
        self.academic_validation.validate_lesson_id(data)
        teacher = self.teacher_service.handle_get_teacher_by_id(data)
        
        if 'name' in data:
            teacher.name = data['name']

        #update teacher_info
        if any(key for key in data if key in ['email', 'tel', 'add']):
            self.teacher_service.handle_update_teacher_info(data)

        #update lesson_id
        if data.get('lesson_id') != teacher.lesson_id:
            teacher.lesson_id = data['lesson_id']
            #remove all of teacher_id by year_id out of teach class and re add
            self.academic_teacher_service.handle_update_teaching_class_by_lesson(data)

        #update homeclass
        if 'class_room_id' in data:
            if data['class_room_id'] == None:
                self.academic_teacher_service.handle_remove_home_class(data)
            
            else:
                class_room = self.academic_get_service.handle_get_class_room_by_id(data)
                if class_room.teacher_id:
                    raise DuplicateException('Lớp học đã có giáo viên chủ nhiệm!')
                
                class_room.teacher_id = data['teacher_id']   

        #update teaching class
        if 'teach_class' in data:
            self.academic_validation.validate_year_id(data)
            self.academic_teacher_service.handle_update_teaching_class(data)

        self.db.session.commit()
        return teacher
     
class User_Workflow:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.student_repo = self.repo.student
        self.teacher_repo = self.repo.teacher
        self.user_services = UserService(db, repo)
        self.teacher_services = TeacherService(db, repo)
        self.student_services = StudentServices(db, repo)
        self.activity_log_services = ActivityLog_Service(db, repo)
    
    def handle_update_user_info(self, data):
        if data['role'] in ['Teacher', 'admin']:
            #get teacher by user id
            teacher = self.teacher_repo.get_teacher_by_user({'user_id': data['user_id']})
            #get teacher info by teacher
            data['teacher_id'] = teacher.id
            detail_changes = self.teacher_services.handle_update_teacher_info(data)
        
        else:
            #get student by user id
            student = self.student_repo.get_student_by_user({'user_id': data['user_id']})
            data['student_id'] = student.id
            detail_changes = self.student_services.handle_update_student_info(data)

        #user_id, module, action, target_id, detail
        self.activity_log_services.handle_record_activity_log({'user_id': data['user_id'],
                                                              'module': 'user',
                                                              'action': 'UPDATE',
                                                              'detail': f'chỉnh sửa thông tin {detail_changes}'})
        self.db.session.commit()
        return data

    def handle_show_user_info(self, data):
        if data['role'] in ['Teacher', 'admin']:
            #get teacher by user id
            teacher = self.teacher_repo.get_teacher_by_user({'user_id': data['user_id']})
            #get teacher info by teacher
            data['teacher_id'] = teacher.id
            result = self.teacher_services.handle_show_teacher_info(data)

        else:
            #get student by user id
            student = self.student_repo.get_student_by_user({'user_id': data['user_id']})
            data['student_id'] = student.id
            result = self.student_services.handle_show_student_info(data)

        return result[0]
    
    def process_register_account_for_admin(self, data):
        user_data = self.user_services.new_admin_data_for_user(data)
        user = self.user_services.handle_add_user(user_data)
        data['user_id'] = user.id
        data['lesson_id'] = None
        self.teacher_services.handle_add_teacher(data)
        
        self.db.session.commit()


class Auth_Workflow:
    def __init__(self):
        pass

class Score_Workflow:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo
        self.academic_get_service = AcademicGetService(db, repo)
        self.academic_student_service = Academic_Student_Service(db, repo)
        self.academic_score_service = Academic_Score_Service(db, repo)
        self.academic_validation = Academic_Validation(db, repo)
        self.activity_log_service = ActivityLog_Service(db, repo)
        self.student_service = StudentServices(db, repo)

    def process_add_scores(self, data, user_id):
        period_id = self.academic_get_service.handle_get_period_id(data)
        detail_change = []
        for item in data['students']:
            #get student les period
            student = self.student_service.handle_get_student_by_id(item)
            student_lesson_period = self.academic_student_service.handle_get_student_lesson_period({'period_id': period_id,
                                                                                                    'student_id': item['student_id'],
                                                                                                    'lesson_id': data['lesson_id']})
            item['student_lesson_period_id'] = student_lesson_period.id
            if 'scores' in item:
                scores = self.academic_score_service.handle_upsert_score(item)
                detail_change.append(f'{student.name} - điểm {scores}')

            if 'note' in item:
                student_lesson_period.note = item['note']
                detail_change.append(f"{student.name} - {item['note']}")
            
        self.activity_log_service.handle_record_activity_log({'user_id': user_id,
                                                              'target_id': [i['student_id'] for i in data['students']],
                                                              'module': 'academic/entity',
                                                              'action': 'UPDATE',
                                                              'detail': f"Cho em {detail_change}"})

        self.db.session.commit()

    def process_show_students_for_give_score(self, data):
        self.academic_validation.validate_lesson_id(data)
        data['period_id'] = self.academic_get_service.handle_get_period_id(data)

        students = self.academic_student_service.handle_show_students_by_class_lesson_period(data)

        result = self.academic_score_service.handle_show_scores_by_students(data, students)

        return result

    def process_summary_semester_lessons_result(self, data, user_id):
        #get stu id, get per id
        period_id = self.academic_get_service.handle_get_period_id(data)
        lesson = self.academic_get_service.handle_get_lesson_by_id(data)
        class_room = self.academic_get_service.handle_get_class_room_by_id(data)
        student_ids = self.student_service.handle_get_student_ids_by_year_and_class_room(data)
        #get stu les per id => sco mới tính
        for student_id in student_ids:
            student_lesson_period = self.academic_student_service.handle_get_student_lesson_period({'student_id': student_id,
                                                                                                       'period_id': period_id,
                                                                                                       'lesson_id': data['lesson_id']})
            
            score, status = self.academic_score_service.handle_get_scores_and_status_for_student_lesson_period(student_lesson_period.id)
            student_lesson_period.total = score
            student_lesson_period.status = status

        self.activity_log_service.handle_record_activity_log({'user_id': user_id,
                                                              'target_id': student_ids,
                                                              'module': 'academic/entity',
                                                              'action': 'UPDATE',
                                                              'detail': f"Tổng kết điểm môn {lesson.lesson} cho lớp {class_room.class_room}"})
        self.db.session.commit()
    
    def process_summary_semester_result(self, data, user_id):
        #get per id + cls id => get stu ids => get all of score of stu => calc 
        class_room = self.academic_get_service.handle_get_class_room_by_id(data)
        self.academic_validation.validate_semester_id(data)
        period_id = self.academic_get_service.handle_get_period_id(data)

        if data['semester'] == 1:
            for student in data['students']:
                self.academic_student_service.handle_record_academic_semester_results({'student_id': student['student_id'],
                                                                                       'conduct': student['conduct'],
                                                                                       'note': student['note'],
                                                                                       'absent_day': student['absent_day'],
                                                                                       'period_id': period_id,
                                                                                       'class_room_id': data['class_room_id']})
            detail_change = f'Tổng kết học kỳ I cho lớp {class_room.class_room}!'

        elif data['semester'] == 2:
            for student in data['students']:
                self.academic_student_service.handle_record_academic_semester_results({'student_id': student['student_id'],
                                                                                       'conduct': student['conduct'],
                                                                                       'note': student['note'],
                                                                                       'absent_day': student['absent_day'],
                                                                                       'period_id': period_id,
                                                                                       'class_room_id': data['class_room_id']})

            #Sau khi tổng kết HK II sẽ tổng kết các môn học cho cả năm
            self.academic_student_service.handle_record_academic_annual_result(data)
            detail_change = f'Tổng kết học kỳ II và cả năm cho lớp {class_room.class_room}!'

        self.activity_log_service.handle_record_activity_log({'user_id': user_id,
                                                              'target_id': class_room.id,
                                                              'module': 'academic/entity',
                                                              'action': 'UPDATE',
                                                              'detail': detail_change})
        
        self.db.session.commit()

    def process_summary_year_result(self, data, user_id):
        self.academic_validation.validate_year_id(data)
        class_room = self.academic_get_service.handle_get_class_room_by_id(data)

        for student in data['students']:
            self.academic_student_service.handle_record_academic_year_result({'student_id': student['student_id'],
                                                                              'conduct': student['conduct'],
                                                                              'note': student['note'],
                                                                              'absent_day': student['absent_day'],
                                                                              'year_id': data['year_id'],
                                                                              'class_room_id': data['class_room_id']})
            
        self.activity_log_service.handle_record_activity_log({'user_id': user_id,
                                                        'target_id': class_room.id,
                                                        'module': 'academic/entity',
                                                        'action': 'UPDATE',
                                                        'detail': f"Tổng kết cuối năm cho học sinh lớp {class_room.class_room}"})
        
        self.db.session.commit()

class Academic_Relation_Workflow:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.academic_validation = Academic_Validation(db, repo)
        self.academic_get_service = AcademicGetService(db, repo)
        self.academic_relation_service = Academic_Relation_Service(db, repo)
        self.activity_log_service = ActivityLog_Service(db, repo)

    def process_update_lesson(self, data, user_id):
        detail_changes = []
        for item in data:
            current_info = self.academic_get_service.handle_get_lesson_by_id(item)

            if item.get('lesson'):
                self.academic_validation.check_dup_lesson(item)                
                current_info.lesson = item['lesson']

            if any(key in item for key in ['is_folder', 'is_schedule', 'is_visible', 'grade']):
                current_tag = self.academic_get_service.handle_get_lesson_tag_by_lesson(item)

                if 'is_folder' in item:
                    current_tag.is_folder = item['is_folder']

                if 'is_schedule' in item:
                    current_tag.is_schedule = item['is_schedule']

                if 'grade' in item and 'is_visible' in item:
                    #check grade id, year_id
                    self.academic_validation.validate_grade(item)
                    self.academic_validation.validate_year_id(item)
                    #update new grade id
                    current_info.grade = item['grade']
                    current_tag.is_visible = item['is_visible']

                    if current_tag.is_visible == False:
                        if item.get('is_visible') == True:
                            #get year_id and lesson_id, grade of lesson to call create lessons class
                            self.academic_relation_service.create_lessons_class(item['year_id'], item['lesson_id'], current_info.grade)

                    else:
                        if item.get('is_visible') == False:
                            #delete all of rows with lesson id and year id
                            self.academic_relation_service.handle_remove_lessons_class(item)

                elif 'grade' in item and 'is_visible' not in item:
                    #check grade id, year_id
                        self.academic_validation.validate_grade(item)
                        self.academic_validation.validate_year_id(item)
                        #update new grade id
                        current_info.grade = item['grade']

                        if current_tag.is_visible == True:
                            #delete all of rows with lesson id and year id
                            self.academic_relation_service.handle_remove_lessons_class(item)
                            #get year_id and lesson_id, grade of lesson to call create lessons class
                            self.academic_relation_service.create_lessons_class(item['year_id'], item['lesson_id'], current_info.grade)
         
                elif 'grade' not in item and 'is_visible' in item:
                    #check year_id
                    self.academic_validation.validate_year_id(item)
                    current_tag.is_visible = item['is_visible']
                    if item['is_visible'] == True:
                        #get year_id and lesson_id, grade of lesson to call create lessons class
                        self.academic_relation_service.create_lessons_class(item['year_id'], item['lesson_id'], current_info.grade)

                    else:
                        #remove lesson id out of teach_class
                        self.academic_relation_service.handle_remove_lessons_class(item)

            detail_changes.append(current_info.lesson)

        self.activity_log_service.handle_record_activity_log({'user_id': user_id,
                                                              'target_id': [i['lesson_id'] for i in data],
                                                              'module': 'academic/core',
                                                              'action': 'UPDATE',
                                                              'detail': f"Chỉnh sửa môn học {', '.join(detail_changes)}"})
          
        self.db.session.commit()
            
        