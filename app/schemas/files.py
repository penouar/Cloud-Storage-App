from pydantic import BaseModel, Field, ConfigDict

class FileCreate(BaseModel):
    file_name: str = Field(min_length=1, max_length=100)
    file_size: int = Field(gt=0)
    file_type: str = Field(min_length=1, max_length=20)
    folder_id: int | None = None

class FileUpdate(BaseModel):
    file_name: str | None = None
    file_size: int | None = None
    file_type: str | None = None
    folder_id: int | None = None

class FileResponse(BaseModel):
    file_id: int
    file_name: str
    file_size: int
    file_type: str
    folder_id: int | None = None
    user_id: int
    model_config = ConfigDict(from_attributes=True)
