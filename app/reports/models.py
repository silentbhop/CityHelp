from sqlalchemy import ForeignKey, Integer, String, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.db.mixins import TimeStampMixin
from app.reports.enums import ReportStatus


class Report(Base, TimeStampMixin):
    __tablename__ = "reports"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    address: Mapped[str] = mapped_column(String, nullable=False, index=True)
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus),
        default=ReportStatus.REVIEW,
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)

    users = relationship("User", back_populates="reports")
    categories = relationship("Category", back_populates="reports")
    comments = relationship("Comment", back_populates="reports", cascade="all, delete-orphan")