from pydantic import Field, BaseModel, ConfigDict

class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=20)
    email: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=100)

class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    
class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    model_config = ConfigDict(from_attributes=True)
