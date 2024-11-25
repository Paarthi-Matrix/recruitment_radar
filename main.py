from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from models.user import User, Candidate
from passlib.context import CryptContext
from models.schema import UserCreate, UserLogin, CandidateCreate, CandidateSchema, SearchCandidateRequest, \
    UpdateCandidateRequest
from config import SessionLocal, engine, Base
import uvicorn

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
Base.metadata.create_all(bind=engine)
app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/login/")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="Invalid email or password")

    if not pwd_context.verify(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"message": "Login successful", "email": db_user.email}


@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password_hash)
    new_user = User(
        name=user.name,
        email=user.email,
        role=user.role,
        password_hash=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


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
        status=candidate.status,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)

    return {"message": "Candidate created successfully", "candidate": new_candidate}


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
