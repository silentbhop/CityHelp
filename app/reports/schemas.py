from pydantic import BaseModel, Field
from app.reports.enums import ReportStatus


class ReportBase(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=5, max_length=1500)
    address: str = Field(min_length=5, max_length=255)
    category_id: int
    
class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    title: str | None = Field(min_length=3, max_length=100, default=None)
    description: str | None = Field(min_length=5, max_length=1500, default=None)
    address: str | None = Field(min_length=5, max_length=255, default=None)
    category_id: int
    
class ReportStatusUpdate(BaseModel):
    status: ReportStatus

class ReportRead(ReportBase):
    id: int
    user_id: int
    status: ReportStatus
    
    model_config = {
        "from_attributes": True
    }