from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from schemas.factor import FactorCreate, FactorResponse
from services.factor import create_factor, get_all_factors

from models.factor import Factor
from models.models import CandidateFactor, Candidate

router = APIRouter()


@router.post("/create/", response_model=FactorResponse)
def create_new_factor(factor: FactorCreate, db: Session = Depends(get_db)):
    return create_factor(db, factor)


@router.get("/", response_model=List[FactorResponse], summary="Get all factors")
def list_all_factors(db: Session = Depends(get_db)):
    """
    Fetch all companies from the database.
    """
    return get_all_factors(db)


@router.get("/candidates/{candidate_id}")
def get_candidate_and_factors(candidate_id: str, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    candidate_factors = (
        db.query(CandidateFactor)
        .filter(CandidateFactor.candidate_id == candidate_id)
        .join(Factor, CandidateFactor.factor_id == Factor.factor_id)
        .all()
    )

    factors = [
        {"factor_id": factor.factor_id, "factor_name": factor.factor.factor_name, "factor_value": factor.factor_value}
        for factor in candidate_factors
    ]

    # todo need to analise what are the factors required to show to the frontend
    return {
        # "candidate": {
        #     "candidate_id": candidate.candidate_id,
        #     "name": candidate.name,
        #     "email": candidate.email,
        #     "location": candidate.location,
        #     "current_role": candidate.current_role,
        #     "experience_years": candidate.experience_years,
        #     "target_role": candidate.target_role,
        #     "target_industry": candidate.target_industry,
        #     "status": candidate.status.value,
        #     "created_at": candidate.created_at,
        #     "updated_at": candidate.updated_at,
        # },
        "factors": factors,
    }


@router.put("/candidates/{candidate_id}/factors")
def update_candidate_factors(candidate_id: str, factors: list[dict], db: Session = Depends(get_db)):
    candidate_exists = db.query(CandidateFactor).filter(CandidateFactor.candidate_id == candidate_id).first()
    if not candidate_exists:
        raise HTTPException(status_code=404, detail="Candidate not found")

    for factor_data in factors:
        factor = db.query(CandidateFactor).filter(
            CandidateFactor.candidate_id == candidate_id,
            CandidateFactor.factor_id == factor_data["factor_id"]
        ).first()
        if not factor:
            raise HTTPException(
                status_code=404,
                detail=f"Factor with ID {factor_data['factor_id']} not found for candidate {candidate_id}"
            )
        factor.factor_value = factor_data["factor_value"]

    db.commit()
    return {"message": "Candidate factors updated successfully"}
