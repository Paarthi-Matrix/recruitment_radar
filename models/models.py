from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from db import Base


class CandidateStatus(enum.Enum):
    Pending = "Pending"
    Reviewed = "Reviewed"
    PredictionGenerated = "PredictionGenerated"


class Candidate(Base):
    __tablename__ = "candidates"

    candidate_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    location = Column(String(100), nullable=False)
    current_role = Column(String(255), nullable=False)
    experience_years = Column(Float, nullable=False)
    target_role = Column(String(255), nullable=False)
    target_industry = Column(String(100), nullable=False)
    status = Column(Enum(CandidateStatus), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CandidateFactor(Base):
    __tablename__ = "candidate_factors"

    candidate_factor_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = Column(String(36), ForeignKey("candidates.candidate_id"), nullable=False)
    factor_id = Column(String(36), ForeignKey("factors.factor_id"), nullable=False)
    factor_value = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    factor = relationship("Factor", back_populates="candidate_factors")
