from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(min_length=3, max_length=50)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: str | None = Field(min_length=3, max_length=50, default=None)

class CategoryRead(CategoryBase):
    id: int
    model_config = {
        "from_attributes": True
    }