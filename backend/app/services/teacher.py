from app.tasks import send_email_task
from .subservices.sub_teacher import Teacher_Subservices
from app.exceptions import CustomException
from app.utils import generate_password, token_set_password, get_updated_fields
from werkzeug.security import generate_password_hash

class TeacherService:
    def __init__(self, db, user_repo=None, teacher_repo=None, academic_get_repo=None, academic_add_repo=None, academic_update_repo=None):
        self.db = db
        self.teacher_repo = teacher_repo(db)
        self.academic_get_repo = academic_get_repo(db)
        self.academic_add_repo = academic_add_repo(db)
        self.academic_update_repo = academic_update_repo(db)
        self.user_repo = user_repo(db)
        self.teacher_subservices = Teacher_Subservices(self.user_repo, self.teacher_repo, self.academic_get_repo)

    def handle_add_teacher(self, data):
        #check user
        self.teacher_subservices.check_dup_user(data)

        data['password'] = generate_password_hash(generate_password(length=32))
        data['token'] = generate_password_hash(token_set_password(length=32))
        data['role'] = 'Teacher'
        teacher = self.teacher_repo.add_user(data)

        if data['class_room_id']:
            class_room = self.teacher_subservices.check_home_class(data)
            class_room.teacher_id = teacher.id

        #check teach class
        self.teacher_subservices.check_teach_class(data)
        
        data['teacher_id'] = teacher.id
        self.teacher_repo.assign_teach_class(data)
        self.db.session.commit()

        link = f'http://localhost:5173/setpassword?token={data['token']}'
        send_email_task.delay(data['email'], 'Set password', f'Click following link to set password: {link}')
        return data
        
    def handle_show_teacher(self, data):
        result = self.teacher_repo.show_teacher(data)
        keys = ['id', 'name','lesson_id', 'lesson', 'class_room_id', 'class_room', 'teach_room_ids', 'teach_room', 'tel', 'email', 'add', 'status']
        return [dict(zip(keys, values)) for values in result]

    def handle_update_info(self, data):
        current_info_query = self.teacher_repo.get_info(data)
        if not current_info_query:
            raise CustomException('Không truy xuất được dữ liệu') 
        
        keys = ['teacher_id', 'name', 'lesson_id', 'class_room_id','teach_class', 'tel', 'add', 'email', 'year_id']
        current_info = dict(zip(keys, current_info_query))

        update_fields = get_updated_fields(data, current_info)
        if 'name' in update_fields:
            self.teacher_subservices.update_name(data)

        if 'lesson_id' in update_fields:
            self.teacher_subservices.update_lesson(current_info, data)

        if 'add' or 'tel' or 'email' in update_fields:
            self.teacher_subservices.update_info(update_fields, data)

        if 'class_room_id' in update_fields:
            self.teacher_subservices.update_home_class(update_fields, data)

        if 'teach_class' in update_fields:
            self.teacher_subservices.update_teach_class(current_info, data)
            
        self.db.session.commit()
        return current_info
    
    def handle_status_teacher(self, data):
        teacher = self.teacher_repo.get_teacher(data)
        teacher.status = not teacher.status
        self.db.session.commit()
        return teacher
        
    def handle_delete_teacher(self, data):
        self.teacher_repo.delete(data)
        return {'status': 'Success', 'msg': 'Đã xóa giáo viên!'}
        
