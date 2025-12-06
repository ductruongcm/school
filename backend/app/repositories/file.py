from app.models import Class_room, Users, Files, Lesson, Teach_class, LessonTag, Teachers
from .base import BaseRepo

class CloudRepo(BaseRepo):
    def upload(self, data: dict):
        # folder_id, file_name, file_type, file_size, user_id
        fields = self.filter_context('folder_id', 'filename', 'filetype', 'filesize', 'upload_by', context=data)
        self.db.session.add(Files(**fields))
    
    def existing_file(self, data: dict):
        fields = self.filter_context('folder_id', 'filename', context=data)
        return self.db.session.query(Files).filter(Files.folder_id == fields["folder_id"],
                                                   Files.filename == fields["filename"]).scalar()
    
    def show_file(self, data: dict):
        fields = self.filter_context('folder_id', context=data)
        return self.db.session.query(Files.id,
                                    Files.filename,
                                    Files.filetype,
                                    Files.filesize,
                                    Files.upload_at,
                                    Users.username,
                                    Files.file_status,
                                    ).join(Users).filter(Files.folder_id == fields['folder_id']).order_by(Files.upload_at).all()
      
    def delete(self, data: dict):
        self.db.session.query(Files).filter(Files.id == data['file_id']).delete(synchronize_session = False)

    def file_by_id(self, data: dict):
        return self.db.session.query(Files).filter(Files.id == data['file_id']).first()
    
    def download(self, data:dict):
        return self.db.session.query(Class_room.class_room, Lesson.lesson, Files.filename)\
                                    .join(Files.teach_class)\
                                    .outerjoin(Teach_class.class_room)\
                                    .outerjoin(Teach_class.lesson).filter(Files.id == data['file_id']).first()
    
    def folder_id(self, data: dict):
        fields = self.filter_context('class_room_id', 'lesson_id', 'year_id', context=data)
        return self.db.session.query(Teach_class.id).filter(Teach_class.class_room_id == fields['class_room_id'],
                                                            Teach_class.lesson_id == fields['lesson_id'],
                                                            Teach_class.year_id == fields['year_id']).scalar()
    
    def file_info_by_id(self, data: dict):
        fields = self.filter_context('file_id', context=data)
        return self.db.session.query(Class_room.class_room,
                                     Lesson.lesson,
                                     Files.filename).join(Files.teach_class)\
                                                    .join(Teach_class.class_room)\
                                                    .join(Teach_class.lesson)\
                                                        .filter(Files.id == fields['file_id']).first()
    
    def show_folder_for_teacher(self, data):
        return (self.db.session.query(Teach_class.lesson_id, Lesson.lesson)
                               .join(Teach_class.lesson)
                               .join(Teach_class.teachers)
                               .join(Teachers.users).filter(Teach_class.year_id == data['year_id'],
                                                            Teach_class.class_room_id == data['class_room_id'],
                                                            Users.id == data['user_id']).all())

    def show_folders_for_student_and_admin(self, data):
        return (self.db.session.query(Lesson.id, Lesson.lesson)
                    .join(Class_room, Class_room.grade >= Lesson.grade)
                    .join(Lesson.lessontag)
                    .filter(Class_room.id == data['class_room_id'],
                            LessonTag.is_folder == True).all())