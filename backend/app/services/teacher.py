from app.tasks import send_email_task
from .subservices.sub_teacher import Teacher_Subservices
from app.exceptions import NotFound_Exception

class TeacherService:
    def __init__(self, db, repo):
        self.db = db
        self.repo = repo(db)
        self.teacher_repo = self.repo.teacher
        self.teacher_subservices = Teacher_Subservices(self.teacher_repo)

    def handle_get_teacher_by_id(self, data):
        teacher = self.teacher_repo.get_teacher_by_id(data)
        if not teacher:
            raise NotFound_Exception('Không tìm thấy teacher!')
        
        return teacher
    
    def handle_get_teacher_by_user(self, data):
        teacher = self.teacher_repo.get_teacher_by_user(data)
        if not teacher:
            raise NotFound_Exception('Không tìm thấy teacher!')
        
        return teacher
    
    def handle_get_teacher_info_by_teacher(self, data):
        teacher_info = self.teacher_repo.get_teacher_info_by_teacher(data)
        if not teacher_info:
            raise NotFound_Exception('Không tìm thấy teacher info!')
        return teacher_info

    def handle_add_teacher(self, data):    
        teacher = self.teacher_repo.add_teacher({'user_id': data['user_id'],
                                                 'name': data['name'],
                                                 'lesson_id': data['lesson_id'],
                                                 'email': data['email'],
                                                 'tel': data['tel'],
                                                 'add': data['add']})
        return teacher
        
    def send_set_password_mail(self, data):    
        link = f'http://localhost:5173/setpassword?token={data['token']}'
        body = f"""
Xin chào {data['name']},

Tài khoản của bạn đã được tạo tại hệ thống trường BVD.

Vui lòng nhấn vào liên kết sau để đặt mật khẩu (hiệu lực trong 7 giờ):
{link}

Trân trọng,
Phòng quản trị hệ thống
(Đây là email tự động, vui lòng không trả lời.)
"""
        send_email_task.delay(data['email'], 'Set password', body.encode('utf-8').decode('utf-8'))
        
    def handle_update_teacher_info(self, data):
        if any(key for key in data if key in ['email', 'tel', 'add']):
            detail_changes = []
            teacher_info = self.teacher_repo.get_teacher_info_by_teacher(data)
            if not teacher_info:
                raise NotFound_Exception('ID giáo viên không hợp lệ!')
            
            if data.get('email'):
                old_email = teacher_info.email
                teacher_info.email = data['email']
                detail_changes.append(f'email: {old_email} => {data['email']}')

            if data.get('tel'):
                old_tel = teacher_info.tel
                teacher_info.tel = data['tel']
                detail_changes.append(f'SĐT: {old_tel} => {data['tel']}')

            if data.get('add'):
                old_add = teacher_info.add
                teacher_info.add = data['add']
                detail_changes.append(f'Địa chỉ: {old_add} => {data['add']}')
            
            return ', '.join(detail_changes)
                
    def handle_show_teachers(self, data):
        result = self.teacher_repo.show_teachers(data)
        keys = ['id', 'name','lesson_id', 'lesson', 'class_room_id', 'class_room', 'teach_room_ids', 'teach_room', 'tel', 'email', 'add', 'status']
    
        return [dict(zip(keys, values)) for values in result]
   
    def handle_status_teacher(self, data):
        teacher = self.teacher_repo.get_teacher_by_id(data)
        teacher.status = not teacher.status
        self.db.session.commit()
        return teacher
        
    def handle_delete_teacher(self, data):
        self.teacher_repo.delete(data)
        return {'status': 'Success', 'msg': 'Đã xóa giáo viên!'}
        
    def handle_show_teacher_info(self, data):
        result = [self.teacher_repo.show_teacher_info_by_user(data)]
        keys = ['name', 'email', 'tel', 'add']
        return [dict(zip(keys, values)) for values in result]