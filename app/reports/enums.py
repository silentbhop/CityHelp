from enum import Enum

class ReportStatus(str, Enum):
    REVIEW = "review"
    PENDING = "pending"
    RESOLVED = "resolved"