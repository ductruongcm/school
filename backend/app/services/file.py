from app.exceptions import NotFound_Exception
from .subservices.sub_file import File_Subservices
from .base import BaseService
from app.utils.storage import minio

class CloudService(BaseService):
    def __init__(self, db, repo):
        super().__init__(db)
        self.repo = repo(db)
        self.file_subservices = File_Subservices(self.repo)

    def handle_upload(self, data: dict):             
        file_ext = data['file_ext'].split('.')[1]
        data['filename'] = data['filename'] + f'.{file_ext}'
        data['folder_id'] = self.file_subservices.folder_id(data)

        self.file_subservices.dup_filename(data)

        self.repo.upload(data)
        self.db.session.commit()
        url = minio.cloud_upload(data['class_room'], data['folder'], data['filename'])
        return {'url': url, 'filename': data['filename']}
        
    def handle_show_file(self, data):
        data['folder_id'] = self.file_subservices.folder_id(data)
        result = self.repo.show_file(data)
        keys = ['id', 'file_name', 'file_type', 'file_size', 'upload_at', 'upload_by', 'status']
        return [dict(zip(keys, values)) for values in result]

    def handle_download(self, data):
        file = self.file_subservices.download(data)
        url = minio.cloud_download(file.class_room, file.lesson, file.filename)
        if not url: 
            raise NotFound_Exception('Link không còn hữu hiệu!')
        
        return url
    
    def handle_status(self, data):
        file = self.file_subservices.file_by_id(data)
        
        file.file_status = not file.file_status
        self.db.session.commit()
        return {'id': file.id, 'filename': file.filename, 'status': file.file_status}
        
    def handle_delete(self, data):
        file = self.file_subservices.file_info_by_id(data)

        minio.cloud_delete(file.class_room, file.lesson, file.filename)
        self.repo.delete(data)
        self.db.session.commit()
        return {'filename': file.filename}

  