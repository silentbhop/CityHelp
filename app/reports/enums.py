from enum import Enum

class ReportStatus(str, Enum):
    REVIEW = "На проверке"
    PENDING = "Ожидает решения"
    RESOLVED = "Решено"