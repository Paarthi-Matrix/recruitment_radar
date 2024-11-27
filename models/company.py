import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship

from db import Base


class Company(Base):
    __tablename__ = "company"

    company_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_name = Column(String(255), nullable=False)
    company_location = Column(String(255), nullable=False)
    company_email = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(tz=timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(tz=timezone.utc),
                        onupdate=lambda: datetime.now(tz=timezone.utc))

    # Relationship to users
    users = relationship("User", back_populates="company")
    # Relationship with CompanyFactor
    company_factors = relationship("CompanyFactor", back_populates="company")


class CompanyFactor(Base):
    __tablename__ = "company_factors"

    company_factor_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("company.company_id"), nullable=False)
    factor_id = Column(String(36), ForeignKey("factors.factor_id"), nullable=False)
    weightage = Column(Float, nullable=False, default=1.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="company_factors")
    factor = relationship("Factor", back_populates="company_factors")

