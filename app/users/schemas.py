from pydantic import BaseModel, Field
from app.users.enums import UserRole


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=30)

class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)
    
class UserRead(UserBase):
    id: int
    role: UserRole
    
    model_config = {
        "from_attributes": True
    }