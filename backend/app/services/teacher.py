from app.schemas import ValidationError, TeacherSchemas
from app.repositories import Teacher_repo, User_repo, Academic_repo, Class_room_repo
from app.tasks import send_email_task
from app.utils import error_400, error_422, generate_password, token_set_password, get_updated_fields
from werkzeug.security import generate_password_hash
from app.extensions import db

class Teacher_service:
    @staticmethod
    def handle_add_teacher(data):
        try:
            teacher_data = TeacherSchemas.TeacherCreateSchema(**data)
        except ValidationError as e:
            return error_422(e)
        
        if User_repo.get_user(teacher_data.username):
            return error_400('Username đã được sử dụng!')
        
        lesson = Academic_repo.Get_repo.get_lesson(teacher_data.lesson)
        if not lesson:
            return error_400('Không tìm thấy môn học')
            
        try:           
            password = generate_password(length = 32)
            token = generate_password_hash(token_set_password(length = 32))
            teacher = Teacher_repo.add_user(teacher_data.username, 
                                            password, 
                                            token, 
                                            teacher_data.name, 
                                            lesson.id,
                                            teacher_data.email,
                                            teacher_data.tel,
                                            teacher_data.add)
            
            repo = Class_room_repo(teacher_data.year)
            if teacher_data.class_room:
                class_room = repo.get_class_room(teacher_data.class_room)
                if class_room.teacher_id:
                    raise ValueError('Lớp học đã có giáo viên chủ nhiệm!')
                
                class_room.teacher_id = teacher.id
            teach_room = [repo.get_class_room(room).id for room in teacher_data.teach_room]

            check_teach_room = [repo.check_teach_room(lesson.id, room) for room in teach_room]
            if all(check_teach_room):
                raise ValueError('Lớp học đã có giáo viên bộ môn này!!')
            
            repo.assign_teach_rooms(teacher.id, teacher_data.teach_room)
            db.session.commit()

            link = f'http://localhost:5173/setpassword?token={token}'
            send_email_task.delay(teacher_data.email, 'Set Password', f'Click following link to set password: {link}')

            return {'status': 'ok', 'msg': 'Thêm giáo viên thành công'}
        
        except Exception as e:
            db.session.rollback()
            return {'status': 'DB_error', 'msg': f'DB_error: {str(e)}'}
        
    @staticmethod
    def handle_show_teacher(data):
        try:
            teacher_data = TeacherSchemas.TeacherShowSchema(**data)
        except ValidationError as e:
            return error_422(e)
        
        try:
            rows = Teacher_repo.show_teacher(teacher_data.lesson, teacher_data.class_room, teacher_data.name)
            if rows:
                keys = ['id', 'name', 'lesson', 'class_room', 'teach_room', 'tel', 'email', 'add']
                return {'status': 'ok', 'data': [dict(zip(keys, values)) for values in rows]}
 
            else:
                return {'status': 'Logic_error', 'msg': 'Không tìm thấy thông tin!'}
            
        except Exception as e:
            return {'status': 'DB_error', 'msg': f'DB_error: {str(e)}'}

    @staticmethod
    def handle_update_info(data):
        try:
            update_info_data = TeacherSchemas.TeacherUpdateSchema(**data)

        except ValidationError as e:
            return error_422(e)
        
        if not Academic_repo.Get_repo.get_lesson(update_info_data.lesson):
            return error_400('Thông tin môn học không hợp lệ!')
        
        query = Teacher_repo.Get_repo.get_info(update_info_data.id, update_info_data.year)
        keys = ['id', 'name', 'lesson', 'class_room', 'class_room_id','teach_room', 'tel', 'add', 'email', 'year']
        current_info = dict(zip(keys, query))  
        
        update = get_updated_fields(data, current_info)
        repo = Class_room_repo(update_info_data.year)
        if update.get('name'):
            Teacher_repo.Get_repo.get_teacher(update_info_data.id).name = update_info_data.name

        if update.get('lesson'):
            lesson_id = Academic_repo.Get_repo.get_lesson(update_info_data.lesson).id
            Teacher_repo.Get_repo.get_teacher(update_info_data.id).lesson_id = lesson_id

        if update.get('class_room'):
            class_room = repo.get_class_room(update_info_data.class_room)
            class_room.teacher_id = update_info_data.id

        if update.get('teach_room'):
            lesson_id = Academic_repo.Get_repo.get_lesson(update_info_data.lesson).id
            rooms = [repo.get_class_room(i) for i in update_info_data.teach_room.replace(' ','').split(',')]
            if not all(rooms):
                return error_400('Thông tin lớp học không hợp lệ!')
            
            new_teach_room = {room.id for room in rooms}
                
            current_teach_room = set(repo.get_teach_room(update_info_data.id))
            to_del = current_teach_room - new_teach_room
            to_add = new_teach_room - current_teach_room

            error = [repo.check_teach_room(lesson_id, i) for i in to_add]
            if all(error):
                return error_400('Đã có giáo viên bộ môn cho lớp này!')

            repo.update_teach_room(update_info_data.id, to_del, to_add)
     
        
        if update.get('tel'):
            Teacher_repo.Get_repo.get_teacher_info(update_info_data.id).tel = update['tel']

        if update.get('add'):
            Teacher_repo.Get_repo.get_teacher_info(update_info_data.id).add = update['add']

        if update.get('email'):
            Teacher_repo.Get_repo.get_teacher_info(update_info_data.id).email = update['email']

        db.session.commit()
        return {'status': 'success', 'msg': 'Đã cập nhật thông tin!'}

