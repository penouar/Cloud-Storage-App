from pydantic import BaseModel, Field, ConfigDict
from .permission import PermissionType

class FileShareCreate(BaseModel):
    file_id: int
    to_user_id: int
    permission: PermissionType 

class FileShareUpdate(BaseModel):
    permission: PermissionType | None = None

class FileShareResponse(BaseModel):
    file_id: int
    to_user_id: int
    permission: PermissionType
    model_config = ConfigDict(from_attributes=True)