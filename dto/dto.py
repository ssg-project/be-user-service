from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

### user
class UserLoginReqeust(BaseModel):
    email: str
    password: str

class UserJoinRequest(BaseModel):
    email: str
    password: str

class UserDeleteRequest(BaseModel):
    user_id: int

### file    
class FileUploadedItem(BaseModel):
    file_name: str
    file_content: bytes
    
class FileUploadRequest(BaseModel):
    files: List[FileUploadedItem]

class FileDeleteRequest(BaseModel):
    file_ids: List[int]

class FileItem(BaseModel):
    id: int
    file_key: str
    file_url: str
    created_at: datetime
    
class GetFileListResponse(BaseModel):
    data: List[FileItem]

class Test(BaseModel):
    files: List[bytes]

### auth
class RefreshTokenRequest(BaseModel):
    refresh_token: str