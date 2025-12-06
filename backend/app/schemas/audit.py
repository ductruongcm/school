from pydantic import BaseModel, field_validator, Field
from datetime import date, datetime
from typing import Optional, Union
import re

class AuditShowSchema(BaseModel):
    ip: Optional[str] = None
    username: Optional[str] = None
    action: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[Union[date, str]] = None
    end_date: Optional[Union[date, str]] = None
    page: Optional[int] = None

    @field_validator('username')
    def username_validator(cls, v):
        if not v:
            return 
        elif not re.match(r'^[a-z0-9_]{8,}$', v):
            raise ValueError('Username không hợp lệ!')
        return v

    @field_validator('status')
    def status_validator(cls, v):
        if not v:
            return 
        elif v not in ['SUCCESS', 'FAIL']:
            raise ValueError('Status không hợp lệ!')
        return v
    
    @field_validator('action')
    def action_validator(cls, v):
        if not v:
            return 
        elif re.search(r'[\d`~!@#$%^&*(_)=+,.<>/?;:-]', v):
            raise ValueError('Action không hợp lệ!')
        return v
    
    @field_validator('ip')
    def ip_validator(cls, v):
        if not v:
            return 
        elif re.fullmatch(r'(\d{1,3}\.){3}\d{1,3}', v):
            raise ValueError('IP không hợp lệ!')
        return v
    
    @field_validator('page', mode = 'before')
    def page_validator(cls, v):
        if not v or v == '':
            raise ValueError('Page không được để trống!')
        elif not re.fullmatch(r'[\d]+', v):
            raise ValueError('Page không hợp lệ!')
        return v
    
    @field_validator('start_date', 'end_date', mode = 'before')
    def normalize_date(cls, v):
        if not v or v == '':
            return 
        if isinstance(v, str):
            return datetime.strptime(v, '%Y-%m-%d').date()
        return v

    @field_validator('end_date')
    def end_date_validator(cls, v: Optional[date]):
        if v and v > datetime.utcnow().date():
            raise ValueError('End date không hợp lệ!')
        return v
    
class ActivityShowSchema(BaseModel):
    username: Optional[str] = Field(default=None)
    action: Optional[str] = Field(default=None)
    module: Optional[str] = Field(default=None)
    start_date: Optional[Union[date, str]] = Field(default=None)
    end_date: Optional[Union[date, str]] = Field(default=None)
    page: Optional[int] = Field(default=None)

    @field_validator('start_date', 'end_date', 'page', mode='before')
    def validate_space(cls, v):
        if v in ['', 'null']:
            return 
        
        return v
    