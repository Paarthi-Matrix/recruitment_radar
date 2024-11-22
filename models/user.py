import enum
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
)
from sqlalchemy.orm import relationship

from config import Base


class UserRole(enum.Enum):
    admin = "Admin"
    recruiter = "Recruiter"


class FactorType(enum.Enum):
    Personal = "Personal"
    Compensation = "Compensation"
    Psychological = "Psychological"
    RoleSpecific = "RoleSpecific"


class CandidateStatus(enum.Enum):
    Pending = "Pending"
    Reviewed = "Reviewed"
    PredictionGenerated = "PredictionGenerated"


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Candidate(Base):
    __tablename__ = "candidates"

    candidate_id = Column(Integer, primary_key=True, autoincrement=True)
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


class Factor(Base):
    __tablename__ = "factors"

    factor_id = Column(Integer, primary_key=True, autoincrement=True)
    factor_name = Column(String(255), unique=True, nullable=False)
    factor_description = Column(Text, nullable=True)
    factor_type = Column(Enum(FactorType), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidate_factors = relationship("CandidateFactor", back_populates="factor")


class CandidateFactor(Base):
    __tablename__ = "candidate_factors"

    candidate_factor_id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.candidate_id"), nullable=False)
    factor_id = Column(Integer, ForeignKey("factors.factor_id"), nullable=False)
    factor_value = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    factor = relationship("Factor", back_populates="candidate_factors")
