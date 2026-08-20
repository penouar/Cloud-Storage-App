from pydantic import BaseModel, Field, ConfigDict
from .permission import PermissionType

class FolderShareCreate(BaseModel):
    folder_id: int
    to_user_id: int
    permission: PermissionType

class FolderShareUpdate(BaseModel):
    permission: PermissionType | None = None

class FolderShareResponse(BaseModel):
    folder_id: int
    to_user_id: int
    permission: PermissionType
    model_config = ConfigDict(from_attributes=True)