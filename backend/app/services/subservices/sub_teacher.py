from app.exceptions import CustomException

class Teacher_Subservices:
    def __init__(self, user_repo, teacher_repo, academic_get_repo):
        self.teacher_repo = teacher_repo
        self.academic_get_repo = academic_get_repo
        self.user_repo = user_repo

    def check_teach_class(self, data):
        check_teach_class = self.teacher_repo.check_teach_class(data)
        if bool(any(check_teach_class)): 
            raise CustomException('Lớp học đã có giáo viên bộ môn này!')
        
    def check_home_class(self, data):
        home_class = self.academic_get_repo.class_room_by_id(data)
        if home_class:
            raise CustomException(f"Lớp {data['class_room']} đã có giáo viên chủ nhiệm!")
        
        return home_class

    def check_dup_user(self, data):
        user = self.user_repo.get_user(data)
        if user:
            raise CustomException('Username đã được sử dụng!')
        
    def update_name(self, update_data):
        teacher = self.teacher_repo.get_teacher(update_data)
        teacher.name = update_data['name']

    def update_info(self, update_fields, update_data):
        info = self.teacher_repo.get_teacher_info(update_data)
        if update_fields.get('add'): info.add = update_data['add']
        if update_fields.get('tel'): info.tel = update_data['tel']
        if update_fields.get('email'): info.email = update_data['email'] 
    
    def update_home_class(self, update_fields, update_data):
        if update_fields.get('class_room_id') == None:
            home_class = self.academic_get_repo.class_room_by_teacher_id(update_data)
            home_class.teacher_id = None
        else:
            home_class = self.academic_get_repo.class_room_by_id(update_data)
            home_class.teacher_id = update_data['teacher_id']

    def update_lesson(self, cur_data, update_data):
        lesson = self.teacher_repo.get_teacher(update_data)
        lesson.lesson_id = update_data['lesson_id']

        classes = self.academic_get_repo.teach_class_by_class_room_id(cur_data) 
        
        for teachclass in classes:
            teachclass.teacher_id = None
    
    def update_teach_class(self, cur_data, update_data):
        new_teach_rooms = set(update_data.get('teach_class'))
        current_teach_rooms = set(self.academic_get_repo.teach_class_id_by_teacher_id(cur_data))
        
        if to_add := new_teach_rooms - current_teach_rooms:
            update_data['teach_class'] = to_add
            #check dup
            self.check_teach_class(update_data)
            
            teach_classes = self.academic_get_repo.teach_class_by_class_room_id(update_data)
            
            for teach_class in teach_classes:
                teach_class.teacher_id = update_data['teacher_id']   

        if to_del:= current_teach_rooms - new_teach_rooms:
            update_data['teach_class'] = to_del
            teach_classes = self.academic_get_repo.teach_class_by_class_room_id(update_data)
            for teach_class in teach_classes:
                teach_class.teacher_id = None

