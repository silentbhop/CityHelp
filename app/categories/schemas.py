from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(min_length=3, max_length=50)

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int
    model_config = {
        "from_attributes": True
    }