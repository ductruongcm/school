from app.utils import filter_fields
from ..base import BaseService
from ..validation import Academic_Validation
from app.exceptions import NotFound_Exception
from ..log import ActivityLog_Service

class AcademicGetService:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.academic_get_repo = self.repo.academic_get

    def handle_get_prev_year_id(self, data):
        year = self.academic_get_repo.get_year_by_id(data)
        if not year:
            raise NotFound_Exception('ID niên khóa không hợp lệ!')
        
        year_code = year.year_code[0:4]
        prev_year_id = self.academic_get_repo.get_prev_year_id({'year_code': year_code})
        if not prev_year_id:
            raise NotFound_Exception('Year code không hợp lệ!')
        
        return prev_year_id
    
    def handle_get_new_year_id(self, data):
        year = self.academic_get_repo.get_year_by_id(data)
        if not year:
            raise NotFound_Exception('Id Niên khóa không hợp lệ!')
        
        year_key_for_search = year.year_code[-4::]
        new_year_id = self.academic_get_repo.get_new_year_id(year_key_for_search)
        if not new_year_id:
            raise NotFound_Exception('Không tìm thấy new year id!')
        
        return new_year_id

    #class
    def handle_get_class_room_by_id(self, data):
        class_room = self.academic_get_repo.get_class_room_by_id(data)
        if not class_room:
            raise NotFound_Exception('ID lớp học không hợp lệ!')

        return class_room
    
    def handle_get_class_room_by_teacher_id(self, data):
        class_room = self.academic_get_repo.get_class_room_by_teacher_id(data)
        if not class_room:
            raise NotFound_Exception('Không tìm thấy class room!')
        return class_room

    def handle_get_teaching_class_by_class_rooms(self, data):
        teaching_classes = self.academic_get_repo.get_teaching_class_by_class_rooms(data)
        if not teaching_classes:
            raise NotFound_Exception('Không tìm thấy teaching class!')
        
        return teaching_classes
    
    def handle_get_teaching_class_by_class_room_year_general_folder(self, data):
        teaching_class = self.academic_get_repo.get_teaching_class_by_class_room_year_general_folder(data)
        if not teaching_class:
            raise NotFound_Exception('Không tìm thấy teaching class!')
        
        return teaching_class
    
    def handle_get_teaching_class_by_teacher_year_general_folder(self, data):
        teaching_class = self.academic_get_repo.get_teaching_class_by_teacher_year_general_folder(data)
        if not teaching_class:
            raise NotFound_Exception('Không tìm thấy teaching class!')
        
        return teaching_class
    #grade
    def handle_get_grade_by_class_room(self, data):
        grade = self.academic_get_repo.get_grade_by_class_room(data)
        if not grade:
            raise NotFound_Exception('Không tìm thấy grade bằng ID của lớp học!')
        
        return grade
    
    def handle_get_grade_by_grade(self, data):
        grade = self.academic_get_repo.get_grade_by_grade(data)
        if not grade:
            raise NotFound_Exception('Không tìm thấy grade bằng ID')
        return grade

    def handle_get_period_id(self, data):
        period_id = self.academic_get_repo.get_period_id(data)
        if not period_id:
            raise NotFound_Exception('Không tìm thấy period bằng ID của year và semester!')
        
        return period_id
    
    def handle_get_period_ids_by_year(self, data):
        period_ids = self.academic_get_repo.get_period_ids_by_year(data)
        if not period_ids:
            raise NotFound_Exception('Không tìm thấy period ids!')
        
        return period_ids
    
    def handle_get_lesson_ids_by_grade_and_is_visible(self, data):
        lesson_ids = self.academic_get_repo.get_lesson_ids_by_grade_and_is_visible({'grade': data['grade']})
        if not lesson_ids:
            raise NotFound_Exception('Không tìm thấy lesson bởi grade id!')
        
        return lesson_ids
    
    def handle_get_lessons_by_grade_and_is_visible(self, data):
        lessons = self.academic_get_repo.get_lessons_by_grade_and_is_visible(data)
        if not lessons:
            raise NotFound_Exception('Không tìm thấy lessons!')
        
        return lessons
    
    def handle_get_lesson_by_id(self, data):
        lesson = self.academic_get_repo.get_lesson_by_id(data)
        if not lesson:
            raise NotFound_Exception('ID lesson không hợp lệ!')
        
        return lesson

    def handle_get_lesson_tag_by_lesson(self, data):
        lesson_tag = self.academic_get_repo.get_lesson_tag_by_lesson(data)
        if not lesson_tag:
            raise NotFound_Exception('không tìm thấy Lesson tag!')
        
        return lesson_tag
    
    def handle_get_year_by_id(self, data):
        year = self.academic_get_repo.get_year_by_id(data)
        if not year:
            raise NotFound_Exception('Không tìm thấy year!')
        return year
    
    def handle_get_semester_by_id(self, data):
        semester = self.academic_get_repo.get_semester_by_id(data)
        if not semester:
            raise NotFound_Exception('Không tìm thấy semester!')
        return semester    
    
    def handle_get_score_type_by_id(self, data):
        score_type = self.academic_get_repo.get_score_type_by_id(data)
        if not score_type:
            raise NotFound_Exception('Không tìm thấy Score type!')
        return score_type
    
    def handle_get_class_rooms_by_year(self, data):
        class_rooms = self.academic_get_repo.get_class_rooms_by_year(data)
        if not class_rooms:
            raise NotFound_Exception('Không tìm thấy class rooms!')
        return class_rooms

class AcademicAddService(BaseService):
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.academic_add_repo = self.repo.academic_add
        self.academic_get_service = AcademicGetService(db, repo)
        self.activity_log_service = ActivityLog_Service(db, repo)
        self.academic_validation = Academic_Validation(db, repo)

    def generate_year_code(self, data):
        start_date = data['start_date'].isoformat()
        end_date = data['end_date'].isoformat()
        return f"{start_date[0:4]} - {end_date[0:4]}"

    def handle_add_year(self, data: dict):      
        #generate year code  
        data['year_code'] = self.generate_year_code(data)
        #check dup year code
        self.academic_validation.check_dup_year({'year_code': data['year_code']})
        #add new_year
        self.academic_add_repo.insert_year(data)
            
        self.db.session.commit()
        return data
         
    def handle_add_semester(self, data: dict):   
        self.academic_validation.check_dup_semester(data)
        semester = self.academic_add_repo.insert_semester({'semester': data['semester'],
                                                           'weight': data['weight']})
        
        self.academic_add_repo.insert_period({'year_id': data['year_id'],
                                              'semester_id': semester.id})
        self.db.session.commit()
        return {'data': semester.semester}
         
    def handle_add_lesson(self, data: dict, user_id):  
        #check dup name      
        self.academic_validation.check_dup_lesson(data)
        #check grade
        self.academic_validation.validate_grade(data)
        #add to lesson and lessontag
        lesson = self.academic_add_repo.insert_lesson(data)
        self.activity_log_service.handle_record_activity_log({'user_id': user_id,
                                                              'module': 'academi/core',
                                                              'action': 'CREATE',
                                                              'detail': f'Tạo môn học {data['lesson']}'})

        self.db.session.commit()
        return lesson
        
    def handle_add_grade(self, data: dict, user_id):       
        self.academic_validation.check_dup_grade(data)

        self.academic_add_repo.insert_grade(data)

        self.db.session.commit()
        return {'data': data['grade']}
  
    def handle_add_class_room(self, data: dict):  
        #check year
        self.academic_validation.validate_year_id(data)
        #check class_room
        self.academic_validation.check_dup_class_room(data)
        
        self.academic_add_repo.insert_class_room(data)
        self.db.session.commit()
        return {'data': data['class_room']}
    
    def handle_add_score_types(self, data, user_id):
        self.academic_validation.check_dup_score_type(data)

        self.academic_add_repo.insert_score_types(data)
        self.activity_log_service.handle_record_activity_log({'user_id': user_id,
                                                              'module': 'academic/core',
                                                              'action': 'CREATE',
                                                              'detail': f"Tạo điểm số {data['score_type']}"})

        self.db.session.commit()

class AcademicShowService(BaseService):
    def __init__(self, db, repo):
        self.repo = repo(db)
        self.show_repo = self.repo.academic_show
        self.academic_validation = Academic_Validation(db, repo)
        self.academic_get_service = AcademicGetService(db, repo)

    def handle_show_year(self, data: dict):
        result = self.show_repo.show_years(data)
        keys = ['id', 'year']
        if result: return [dict(zip(keys, values)) for values in result]

    def handle_show_years_for_student(self, data):
        if data['role'] == 'Student':
            result = self.show_repo.show_years_for_student(data)

        keys = ['id', 'year']
        return [dict(zip(keys, values)) for values in result]

    def handle_show_prev_year_code(self):
        result = [self.show_repo.show_prev_year_code()]
        keys = ['id', 'year_code']
        return [dict(zip(keys, values)) for values in result]

    def handle_show_semester(self, data: dict):
        result = self.show_repo.show_semesters(data)
        keys = ['semester_id', 'semester', 'semester_status']
        return [dict(zip(keys, values)) for values in result]
        
    def handle_show_grade(self, data: dict):
        result = self.show_repo.show_grades(data)
        keys = ['grade', 'grade_status']
        if result: return [dict(zip(keys, values)) for values in result]

    def handle_show_score_types(self):
        result = self.show_repo.show_score_types()
        keys = ['score_type_id', 'score_type', 'weight']

        return [dict(zip(keys, values)) for values in result]
        
    def handle_show_teach_room(self, data: dict):
        if data['role'] == 'admin': 
            result = self.show_repo.show_class_room_by_year_and_grade(data)
        
        elif data['role'] == 'Teacher': 
            result = self.show_repo.show_teach_class_by_user(data) 
        
        keys = ['class_room_id', 'class_room', 'grade', 'teacher_id']
        
        if result: return [dict(zip(keys, values)) for values in result]

    def handle_show_teach_class_with_teacher_id_by_lesson_id(self, data: dict):
        keys = ['class_room_id', 'teacher_id', 'class_room']
        if result := self.show_repo.teach_class_with_teacher_id_by_lesson_id(data):
            return [dict(zip(keys, values)) for values in result]
        
    def handle_show_class_room_by_year_and_grade(self, data):
        #check grade, year_id
        self.academic_validation.validate_grade(data)
        self.academic_validation.validate_year_id(data)

        result = self.show_repo.show_class_room_by_year_and_grade(data)
        keys = ['class_room_id', 'class_room', 'grade']
        return [dict(zip(keys, values)) for values in result]
    
    def handle_show_class_room_for_assignment(self, data):
        #check grade, year_id
        self.academic_validation.validate_grade(data)
        self.academic_validation.validate_year_id(data)
        
        if data.get('status') == 'Lên lớp':
            data['grade'] = data['grade'] + 1
            
        result = self.show_repo.show_class_room_by_year_and_grade(data)
        keys = ['class_room_id', 'class_room']
        return [dict(zip(keys, values)) for values in result]
        
    def handle_show_summary_for_me_by_year(self, year_id, user_id):
        result = self.show_repo.get_summary_for_me_by_year(year_id, user_id)
        keys = ['conduct', 'absent_day', 'score', 'status', 'learning_status']
        output = dict(zip(keys, result))
        return output
              
#show lesson
    def handle_show_lessons(self, data:dict):
        keys = ['lesson_id', 'lesson', 'grade', 'is_visible', 'is_folder', 'is_schedule']
        
        if data['role'] == 'Teacher':
            result = self.show_repo.show_lesson_by_user(data)
            keys = ['lesson_id', 'lesson']

        else:
            result = self.show_repo.show_lessons(data)
        
        return [dict(zip(keys, values)) for values in result]

    
    def handle_show_lessons_by_grade(self, data):
        #lấy grade -1 cho năm ngoài và check 
        self.academic_validation.validate_grade(data)
        result = self.show_repo.show_lessons_by_grade(data)

        keys = ['lesson_id', 'lesson']
        return [dict(zip(keys, values)) for values in result]
    
class AcademicUpdateService(BaseService):
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.academic_relation_repo = self.repo.academic_relation
        self.add_repo = self.repo.academic_add
        self.get_repo = self.repo.academic_get
        self.activity_log_service = ActivityLog_Service(db, repo)
        self.academic_get_service = AcademicGetService(db, repo)
        self.academic_validation = Academic_Validation(db, repo)

    def handle_update_class_room(self, data):
        for new in data:
            #check duplicated name
            self.academic_validation.check_dup_class_room(new)

            #check ID
            class_room = self.get_repo.get_class_room_by_id(new)

            #update to db
            class_room.class_room = new['class_room']
            self.db.session.commit()

            class_room = ', '.join(item['class_room'] for item in data)
        return {'class_room': class_room}
    
    def handle_set_year(self, data: dict):
        #Chuyển tất cả về False
        self.academic_relation_repo.set_year_status_to_false()
        #Chuyển selected year về True
        year = self.get_repo.get_year_by_id(data)
        year.is_active = True
        self.db.session.commit()
        return year
    
    def handle_update_semester(self, data: dict):
        for new in data:
            semester_id = self.get_repo.semester_by_id(new)
            #check dup name
            self.academic_validation.dup_semester(new)

            semester_id.semester = new['semester']
            self.db.session.commit()

            semester = ', '.join(item['semester'] for item in data)
        return {'semester': semester}
    
    def handle_set_semester(self, data: dict):
        self.academic_relation_repo.set_semester_status_to_false()

        semester = self.get_repo.get_semester_by_id(data)
        semester.is_active = True
        self.db.session.commit()
        return semester
    
    def handle_update_grades(self, data):
        for item in data:
            #get grade by grade id
            grade = self.academic_get_service.handle_get_grade_by_grade(item)
            if 'grade_status' in item:
                grade.grade_status = item['grade_status']
            if 'grade' in item:
                grade.grade = item['grade']

        self.db.session.commit()

    def handle_update_score_types(self, data, user_id):
        detail_changes = []
        for item in data:
            #check id
            score_type = self.academic_get_service.handle_get_score_type_by_id(item)
            update = filter_fields('score_type', 'weight', context=item) 

            for keys, values in update.items():
                setattr(score_type, keys, values) 
                detail_changes.append(f'Thay đổi {keys} - {values}')

        self.activity_log_service.handle_record_activity_log({'user_id': user_id,
                                                              'target_id': [i['score_type_id'] for i in data],
                                                              'module': 'academic/core',
                                                              'action': 'UPDATE',
                                                              'detail': f"Cập nhật điểm số: {detail_changes}"})
        
        self.db.session.commit()





        
            


    

             



            

        

