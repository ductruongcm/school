from app.utils import export_to_xml

class ExportService:
    def __init__(self, db, repo):
        self.repo = repo(db)
            
    def handle_export_user_to_xml(self, data):
        result = self.repo.user_list(data)
        class_name = result[0][-1]
        keys = ['Họ và tên', 'Mã SV', 'Giới tính', 'Ngày sinh', 'username', 'Mật khẩu', 'Lớp']
        to_file = [dict(zip(keys, values)) for values in result]
        output = export_to_xml(to_file)
        return output, class_name