from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from models.models import Candidate
from models.schema import CandidateCreate, CandidateSchema, SearchCandidateRequest, \
    UpdateCandidateRequest
from db import get_db
import uvicorn

from routes import company, user, factor

app = FastAPI()

app.include_router(company.router, prefix="/companies", tags=["Companies"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(factor.router, prefix="/factor", tags=["Factors"])


@app.post("/candidates/")
def create_candidate(candidate: CandidateCreate, db: Session = Depends(get_db)):
    if candidate.email:
        db_candidate = db.query(Candidate).filter(Candidate.email == candidate.email).first()
        if db_candidate:
            raise HTTPException(status_code=400, detail="Candidate with this email already exists")

    new_candidate = Candidate(
        name=candidate.name,
        email=candidate.email,
        location=candidate.location,
        current_role=candidate.current_role,
        experience_years=candidate.experience_years,
        target_role=candidate.target_role,
        target_industry=candidate.target_industry,
        status='Pending',
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)
    return {"message": "Candidate created successfully", "candidate_id": new_candidate.candidate_id}


@app.post("/candidates/search", response_model=List[CandidateSchema])
def search_candidates_by_name(
    request: SearchCandidateRequest,
    db: Session = Depends(get_db)
):
    """
    Search for candidates by their name (case-insensitive) using request body.

    Args:
        request (SearchCandidateRequest): The request body containing the name or partial name.
        db (Session): The database session dependency.

    Returns:
        List[CandidateSchema]: A list of candidates matching the search criteria.
    """
    candidates = db.query(Candidate).filter(Candidate.name.ilike(f"%{request.name}%")).all()

    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates found with the given name")

    return candidates


@app.get("/candidates", response_model=List[CandidateSchema])
def get_all_candidates(
        page: int = Query(1, ge=1, description="Page number (must be 1 or greater)"),
        size: int = Query(10, ge=1, le=100, description="Number of candidates per page (1-100)"),
        db: Session = Depends(get_db),
):
    """
    Retrieve all candidates with pagination.

    Args:
        page (int): The current page number.
        size (int): The number of candidates per page.
        db (Session): The database session dependency.

    Returns:
        List[Candidate]: A list of candidates for the current page.
    """
    offset = (page - 1) * size
    candidates = db.query(Candidate).offset(offset).limit(size).all()

    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates found")

    return candidates


@app.put("/candidates/{candidate_id}", response_model=CandidateSchema)
def update_candidate(
    candidate_id: str,
    request: UpdateCandidateRequest,
    db: Session = Depends(get_db)  
):
    """
    Update candidate information by ID.

    Args:
        candidate_id (str): The ID of the candidate to update (UUID format).
        request (UpdateCandidateRequest): The request body containing fields to update.
        db (Session): The database session dependency.

    Returns:
        CandidateSchema: The updated candidate information.
    """
    candidate = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(candidate, field, value)

    # Save changes to the database
    db.commit()
    db.refresh(candidate)

    return candidate



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
