from app.exceptions import NotFound_Exception, DuplicateException

class File_Subservices:
    def __init__(self, repo):
        self.repo = repo

    def file_by_id(self, data):
        file = self.repo.file_by_id(data)
        if not file:
            raise NotFound_Exception('Không tìm thấy file ID!')
        
        return file

    def file_info_by_id(self, data):
        file = self.repo.file_info_by_id(data)
        if not file:
            raise NotFound_Exception('Không tìm thấy file ID!')
        
        return file

    def dup_filename(self, data):
        existing = self.repo.existing_file(data)
        if existing: 
            raise DuplicateException('Tên file bị trùng!')

    def folder_id(self, data):
        folder_id = self.repo.folder_id(data)
        if not folder_id:
            raise NotFound_Exception('Không tìm thấy Folder ID!')
        
        return folder_id
    
    def download(self, data):
        file = self.repo.download(data)
        if not file:
            raise NotFound_Exception('Không tìm thấy file ID!')
        
        return file