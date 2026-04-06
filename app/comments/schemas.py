from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    report_id: int
    
class CommentCreate(CommentBase):
    pass

class CommentRead(CommentBase):
    id: int
    user_id: int
    
    model_config = {
        "from_attributes": True
    }