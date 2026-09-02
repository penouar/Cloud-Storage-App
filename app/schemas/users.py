from pydantic import Field, BaseModel, ConfigDict, model_validator

class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=50)
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

class UserLogin(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str

    @model_validator(mode="after")
    def check_username_or_email(self):
        if not self.username and not self.email:
            raise ValueError("Either username or email is required")

        return self