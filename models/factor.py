import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum
from sqlalchemy.orm import relationship

from db import Base


class FactorType(enum.Enum):
    Personal = "Personal"
    Compensation = "Compensation"
    Psychological = "Psychological"
    RoleSpecific = "role_specific"


class Factor(Base):
    __tablename__ = "factors"

    factor_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    factor_name = Column(String(255), unique=True, nullable=False)
    factor_description = Column(Text, nullable=True)
    # factor_type = Column(Enum(FactorType), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidate_factors = relationship("CandidateFactor", back_populates="factor")
    # Relationship with CompanyFactor
    company_factors = relationship("CompanyFactor", back_populates="factor")

