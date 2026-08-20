from pydantic import BaseModel, Field, ConfigDict

class FolderCreate(BaseModel):
    folder_name: str = Field(min_length=1, max_length=100)
    parent_folder_id: int | None = None

class FolderUpdate(BaseModel):
    folder_name: str | None = None
    parent_folder_id: int | None = None

class FolderResponse(BaseModel):
    folder_id: int
    folder_name: str
    parent_folder_id: int | None = None
    user_id: int
    model_config = ConfigDict(from_attributes=True)
