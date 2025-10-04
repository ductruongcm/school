from pydantic import BaseModel, field_validator
import re

class CloudSchemas:
    class Upload(BaseModel):
        class_room_id: int
        class_room: str
        folder: str
        file_name: str
        file_ext: str
        file_type: str
        file_size: int
        user_id: int
        year: str

        @field_validator('class_room_id')
        def class_room_id_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập thông tin lớp học!')
            return v
        
        @field_validator('class_room')
        def class_room_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập lớp học!')
            elif len(v) != 3:
                raise ValueError('Tên lớp chỉ có 3 ký tự!')
            elif not re.fullmatch(r'[\dA-Z]+', v):
                raise ValueError('Tên lớp chỉ chứa số và chữ in hoa!')
            return v 

        @field_validator('folder')
        def folder_validator(cls, v):
            if not v:
                raise ValueError("Chưa nhập thông tin thư mục môn học!")
            elif re.search(r"[\d~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Thông tin không được chứa số và ký tự đặc biệt!")
            return v

        @field_validator('file_name')
        def file_name_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập file_name!')
            elif not re.fullmatch(r'[\da-z_]+', v):
                raise ValueError('File_name không hợp lệ!')
            return v
        
        @field_validator('year')
        def year_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập niên khóa!')
            elif not re.fullmatch(r'[\d\s-]+', v):
                raise ValueError('Niên khóa không được chứa ký tự đặc biệt và chữ cái. VD: 2025 - 2026')  
            return v
    
    class ShowFolderSchema(BaseModel):
        class_room_id: int

    class ShowFileSchema(ShowFolderSchema):
        folder: str

        @field_validator('folder')
        def folder_validator(cls, v):
            if not v:
                raise ValueError("Chưa nhập thông tin thư mục môn học!")
            elif re.search(r"[\d~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Thông tin không được chứa số và ký tự đặc biệt!")
            return v
        
  


