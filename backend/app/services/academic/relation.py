from ..validation import Academic_Validation
from .core import AcademicGetService
from ..log import ActivityLog_Service

class Academic_Relation_Service:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.academic_relation_repo = self.repo.academic_relation
        self.academic_get_repo = self.repo.academic_get
        self.academic_get_service = AcademicGetService(db, repo)
        self.academic_validation = Academic_Validation(db, repo)
        self.activity_log_service = ActivityLog_Service(db, repo)

    def handle_link_lesson_class_by_year(self, data, id):
        # check year_id, get all lesson with is_visible, get all class by grade on lesson and year
        self.academic_validation.validate_year_id(data)
        class_lessons = self.academic_get_repo.get_class_lessons_by_year(data)
        for class_lesson in class_lessons:
            self.academic_relation_repo.insert_lessons_class({'year_id': data['year_id'],
                                                              'lesson_id': class_lesson[1],
                                                              'class_room_id': class_lesson[0]})
                
        self.activity_log_service.handle_record_activity_log({'user_id': id,
                                                              'module': 'academic/relation',
                                                              'action': 'CREATE',
                                                              'detail': 'Tạo liên kết môn học - lớp cho bảng Teach Class'})
        
        self.db.session.commit()
        
    def handle_remove_lessons_class(self, data):
        self.academic_relation_repo.delete_lesson_id_in_teach_class(data)
            
    def handle_add_schedule(self, data: dict, user_id):
        #get class_room, semester, year
        self.academic_validation.validate_class_room_id(data)
        class_room = self.academic_get_service.handle_get_class_room_by_id(data).class_room
        year = self.academic_get_service.handle_get_year_by_id(data).year_code
        semester = self.academic_get_service.handle_get_semester_by_id(data).semester
        #get period_id
        period_id = self.academic_get_service.handle_get_period_id(data)

        for item in data['schedules']:
            item.update({'class_room_id': data['class_room_id'],
                         'period_id': period_id})
            
            if item['lesson_id'] == 0:
                self.academic_relation_repo.delete_schedule(item)

            elif item['lesson_id']:
                self.academic_relation_repo.bulk_upsert_schedule(item)

        self.activity_log_service.handle_record_activity_log({'user_id': user_id,
                                                              'module': 'academic/relation',
                                                              'action': 'CREATE',
                                                              'detail': f"Tạo thời khóa biểu niên khóa {year} - {semester} - lớp {class_room}"})
        self.db.session.commit()
   
    def handle_show_schedules(self, data):
        #check class_room_id, year_id, semester_id
        self.academic_validation.validate_semester_id(data)
        self.academic_validation.validate_year_id(data)
        self.academic_validation.validate_class_room_id(data)
        #get period_id
        data['period_id'] = self.academic_get_service.handle_get_period_id(data)

        result = self.academic_relation_repo.show_schedules(data)
        keys = ['lesson_id', 'day', 'period']
        return [dict(zip(keys, values)) for values in result]