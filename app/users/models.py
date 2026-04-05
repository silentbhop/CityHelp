from sqlalchemy import Integer, String, DateTime, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.db.mixins import TimeStampMixin
from app.users.enums import UserRole


class User(Base, TimeStampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.USER,
        nullable=False
    )
    
    comments = relationship("Comment", back_populates="user")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")
    