import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Column, Float, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from db import Base


class CandidateStatus(str, enum.Enum):
    Pending = "pending"
    Incomplete = "incomplete"
    Reviewed = "reviewed"
    Predicting = "predicting"


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

    # Relationship with CandidatePrediction
    predictions = relationship("Summary", back_populates="candidate")


class CandidateFactor(Base):
    __tablename__ = "candidate_factors"

    candidate_factor_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = Column(String(36), ForeignKey("candidates.candidate_id"), nullable=False)
    factor_id = Column(String(36), ForeignKey("factors.factor_id"), nullable=False)
    factor_value = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    factor = relationship("Factor", back_populates="candidate_factors")
