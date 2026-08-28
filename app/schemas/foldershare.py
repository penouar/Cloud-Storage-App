from pydantic import BaseModel, Field, ConfigDict
from app.models.permission import PermissionType

class FolderShareCreate(BaseModel):
    to_user_id: int
    permission: PermissionType

class FolderShareUpdate(BaseModel):
    permission: PermissionType 

class FolderShareResponse(BaseModel):
    folder_id: int
    to_user_id: int
    permission: PermissionType
    model_config = ConfigDict(from_attributes=True)