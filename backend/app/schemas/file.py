from pydantic import BaseModel, field_validator
from typing import Optional
import re

class CloudSchemas:
    class Upload(BaseModel):
        class_room_id: int
        class_room: str
        folder: str
        filename: str
        file_ext: str
        filetype: str
        filesize: int
        lesson_id: int
        year_id: int

        @field_validator('class_room_id')
        def class_room_id_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập thông tin lớp học!')
            return v

        @field_validator('folder')
        def folder_validator(cls, v):
            if not v:
                raise ValueError("Chưa nhập thông tin thư mục môn học!")
            elif re.search(r"[\d~!@#$%^&*()_+=`,.<>/?-]+", v):
                raise ValueError("Thông tin không được chứa số và ký tự đặc biệt!")
            return v

        @field_validator('filename')
        def file_name_validator(cls, v):
            if not v:
                raise ValueError('Chưa nhập file_name!')
            elif not re.fullmatch(r'[\da-z_A-Z]+', v):
                raise ValueError('File_name không hợp lệ!')
            return v
    
    class ShowFolderSchema(BaseModel):
        class_room_id: Optional[int] | None
        year_id: Optional[int] | None
        grade_id: Optional[int] | None

    class ShowFileSchema(BaseModel):
        lesson_id: Optional[int] | None
        class_room_id: Optional[int] | None
        year_id: int

        @field_validator('lesson_id', 'class_room_id', mode='before')
        def parse_null_int(cls, v):
            if v in ['', 'null', 'None']:
                return None
            return v

    
  


