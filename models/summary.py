import uuid
from datetime import datetime

from sqlalchemy import Column, String, ForeignKey, DateTime, Float, Text
from sqlalchemy.orm import relationship

from db import Base


class Summary(Base):
    __tablename__ = "summary"

    prediction_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = Column(String(36), ForeignKey("candidates.candidate_id"), nullable=False)
    probability_percentage = Column(Float, nullable=False)  # Probability score (e.g., 85.5%)
    probability_summary = Column(Text, nullable=False)  # AI-generated summary for the prediction
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    candidate = relationship("Candidate", back_populates="predictions")
