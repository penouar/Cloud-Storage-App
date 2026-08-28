from pydantic import BaseModel, Field, ConfigDict
from app.models.permission import PermissionType

class FileShareCreate(BaseModel):
    file_id: int
    to_user_id: int
    permission: PermissionType 

class FileShareUpdate(BaseModel):
    permission: PermissionType

class FileShareResponse(BaseModel):
    file_id: int
    to_user_id: int
    permission: PermissionType
    model_config = ConfigDict(from_attributes=True)