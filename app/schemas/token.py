from pydantic import Field, BaseModel, ConfigDict, model_validator

class Token(BaseModel):
    access_token: str
    token_type: str