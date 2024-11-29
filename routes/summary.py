from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from db import get_db
from models.summary import Summary
from models.candidate import Candidate

router = APIRouter()

@router.get("/predictions/latest/")
def get_latest_prediction_summaries(db: Session = Depends(get_db)):
    # Subquery to get the latest prediction for each candidate
    subquery = (
        db.query(
            Summary.candidate_id,
            func.max(Summary.created_at).label("latest_created_at")
        )
        .group_by(Summary.candidate_id)
        .subquery()
    )

    # Join with CandidatePrediction to get full details of the latest prediction
    latest_predictions = (
        db.query(
            Summary.candidate_id,
            Summary.probability_percentage,
            Summary.probability_summary,
            Summary.created_at,
            Candidate.name.label("candidate_name"),
            Candidate.status.label("candidate_status")
        )
        .join(subquery,
              (Summary.candidate_id == subquery.c.candidate_id) &
              (Summary.created_at == subquery.c.latest_created_at))
        .join(Candidate, Summary.candidate_id == Candidate.candidate_id)
        .all()
    )

    # Format the result for response
    results = [
        {
            "candidate_id": pred.candidate_id,
            "candidate_name": pred.candidate_name,
            "probability_percentage": pred.probability_percentage,
            "probability_summary": pred.probability_summary,
            "created_at": pred.created_at,
            "status": pred.candidate_status,
        }
        for pred in latest_predictions
    ]

    return {"latest_predictions": results}
