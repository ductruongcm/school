from app.repositories import CloudRepositories
from app.schemas import CloudSchemas, ValidationError
from app.utils import error_400, error_422, cloud
from app.extensions import db
import traceback

class CloudService:
    @staticmethod
    def handle_upload(data):
        try:
            upload_data = CloudSchemas.Upload(**data)

        except ValidationError as e:
            return error_422(e)
        
        try:
            file_ext = upload_data.file_ext.split('.')[1]
            file_name = upload_data.file_name + f'.{file_ext}'
            if CloudRepositories.check_existing_file(upload_data.class_room_id, upload_data.folder, file_name):
                return error_400('File name đã có, hãy đổi tên khác')
        
            CloudRepositories.upload(upload_data.class_room_id,
                            upload_data.folder,
                            file_name,
                            upload_data.file_type,
                            upload_data.file_size,
                            upload_data.user_id
                            )
            
            db.session.commit()
           
            url = cloud.cloud_upload(upload_data.class_room, upload_data.folder, file_name)
       
            return {'status': 'Success', 'url': url}
        
        except Exception as e:
            print('trace', traceback.format_exc())
            db.session.rollback()
            return {'status': 'DB_error', 'msg': f'{str(e)}'}
        
    @staticmethod
    def handle_download(id):
        #Get id 
        file = CloudRepositories.get_file_by_id(id)
        download_url = cloud.cloud_download(file.class_room, file.folder, file.filename)
        if not download_url:
            return error_400('Download URL không tồn tại!')
        
        return download_url
    
    @staticmethod
    def handle_delete(id):
        #Get id
        file = CloudRepositories.get_file_by_id(id)
        if file:
            cloud.cloud_delete(file.class_room, file.folder, file.filename)
            CloudRepositories.delete_file(id) 
            db.session.commit()
            return {'status': 'Success', 'msg': 'Đã xóa file!', 'file_name': file.file_name}
        
        return error_400('Không có dữ liệu file!')
    
    @staticmethod
    def handle_hide(id):
        file = CloudRepositories.update_file(id)
        print(id)
        if file:
            file.file_status = False
            db.session.commit()
            return {'status': 'Success', 'msg': 'Đã ẩn file!'}
        
        return error_400('Không có dữ liệu file!')
    
    @staticmethod
    def handle_undhide(id):
        file = CloudRepositories.update_file(id)
        if file:
            file.file_status = True
            db.session.commit()
            return {'status': 'Success', 'msg': 'Đã hiện file!'}

        return error_400('Không có dữ liệu file!')
    
    @staticmethod
    def handle_show_folder(data):
        try:
            show_folder_data = CloudSchemas.ShowFolderSchema(**data)

        except ValidationError as e:
            return error_422(e)
        
        try:
            data = list(set(CloudRepositories.show_folder(show_folder_data.class_room_id)))
            if not data:
                return error_400('Không tìm thấy thông tin!')
          
            return data

        except Exception as e:
            print('trace', traceback.format_exc())
            return {'status': 'DB_error', 'msg': f'{str(e)}'}
        
    @staticmethod
    def handle_show_file(data):
        try:
            show_file_data = CloudSchemas.ShowFileSchema(**data)

        except ValidationError as e:
            return error_422(e)
        try:
            result = CloudRepositories.show_file(show_file_data.class_room_id, show_file_data.folder)
            if not result:
                return error_400('Không tìm thấy thông tin!')

            keys = ['id', 'file_name', 'file_type', 'file_size', 'upload_at', 'upload_by', 'status']
            return {'status': 'Success', 'data': [dict(zip(keys, values)) for values in result]}
        
        except Exception as e:
            print('trace', traceback.format_exc())
            return {'status': 'DB_error', 'msg': f'{str(e)}'}
