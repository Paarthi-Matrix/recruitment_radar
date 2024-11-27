import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from db import Base



class UserRole(enum.Enum):
    admin = "Admin"
    recruiter = "Recruiter"


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(tz=timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(tz=timezone.utc),
                        onupdate=lambda: datetime.now(tz=timezone.utc))

    # Foreign key to the company
    company_id = Column(String(36), ForeignKey("company.company_id"), nullable=False)

    # Relationship back to company
    company = relationship("Company", back_populates="users")

