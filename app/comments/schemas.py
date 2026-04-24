from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    
class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    text: str | None = Field(min_length=1, max_length=500, default=None)

class CommentRead(CommentBase):
    id: int
    user_id: int
    report_id: int
    
    model_config = {
        "from_attributes": True
    }