from datetime import datetime, timedelta
from typing import List
import uuid
from fastapi import FastAPI, Depends, HTTPException, Query
from io import BytesIO
from fastapi import FastAPI, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import FastAPI, UploadFile, Depends, HTTPException
from models.models import Candidate, CandidateFactor, CandidateStatus
from models.schema import CandidateCreate, CandidateSchema, SearchCandidateRequest, CandidateCreateResponse
from starlette.responses import StreamingResponse

from models.user import User
from passlib.context import CryptContext
from models.schema import UserCreate, UserLogin, CandidateCreate, CandidateSchema, SearchCandidateRequest, \
    UpdateCandidateRequest
from db import get_db
import uvicorn
import pandas as pd

from constant.app_constant import CANDIDATE_FIELDS
from models.company import CompanyFactor
from models.factor import Factor
from routes.user import pwd_context
from utils.jwt_handler import create_access_token, get_current_company_id
from utils.dependencies import require_role, get_current_user
from config import ACCESS_TOKEN_EXPIRE_MINUTES

from routes import company, user, factor

app = FastAPI()
security = HTTPBearer()
app.include_router(company.router, prefix="/companies", tags=["Companies"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(factor.router, prefix="/factor", tags=["Factors"])


@app.post("/candidates/", dependencies=[Depends(require_role(["admin"]))])
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
    return {"message": "Candidate created successfully", "candidate_id": new_candidate.candidate_id}


@app.post("/candidates/search", response_model=List[CandidateSchema], dependencies=[Depends(require_role(["admin"]))])
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


@app.get("/candidates", response_model=List[CandidateSchema], dependencies=[Depends(require_role(["admin"]))])
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


@app.put("/candidates/{candidate_id}", response_model=CandidateSchema, dependencies=[Depends(require_role(["admin"]))])
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

    db.commit()
    db.refresh(candidate)

    return candidate


@app.get("/xlsx")
def get_excel_data(
        token: str = Depends(get_current_company_id),
        db: Session = Depends(get_db),
):
    company_id = token

    factor_ids = db.query(CompanyFactor.factor_id).filter(
        CompanyFactor.company_id == company_id
    ).all()
    factor_ids = [fid[0] for fid in factor_ids]

    if not factor_ids:
        raise HTTPException(status_code=404, detail="No factors found for the company.")

    factor_names = db.query(Factor.factor_name).filter(Factor.factor_id.in_(factor_ids)).all()
    factor_names = [name[0] for name in factor_names]

    columns = CANDIDATE_FIELDS + factor_names
    df = pd.DataFrame(columns=columns)

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=data.xlsx"},
    )


@app.post("/upload-candidates", response_model=List[CandidateCreateResponse])
def upload_candidates(file: UploadFile, db: Session = Depends(get_db)):
    """
    Endpoint to process Excel file and insert candidates and their factors.
    """
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported")

    contents = file.file.read()
    df = pd.read_excel(BytesIO(contents))

    CANDIDATE_COLUMNS = [
        "name", "email", "location", "current_role",
        "experience_years", "target_role", "target_industry"
    ]
    FACTOR_COLUMNS = df.columns[len(CANDIDATE_COLUMNS):]

    candidates_created = []

    for _, row in df.iterrows():
        candidate_data = {col: row[col] for col in CANDIDATE_COLUMNS}
        new_candidate = Candidate(
            candidate_id=str(uuid.uuid4()),
            **candidate_data,
            status="Pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(new_candidate)
        db.commit()
        db.refresh(new_candidate)

        for factor_name in FACTOR_COLUMNS:
            factor = db.query(Factor).filter(Factor.factor_name == factor_name).first()
            if not factor:
                raise HTTPException(
                    status_code=400,
                    detail=f"Factor '{factor_name}' does not exist in the database."
                )

            candidate_factor = CandidateFactor(
                candidate_factor_id=str(uuid.uuid4()),
                candidate_id=new_candidate.candidate_id,
                factor_id=factor.factor_id,
                factor_value=str(row[factor_name]),
                created_at=datetime.utcnow(),
            )
            db.add(candidate_factor)

        db.commit()
        candidates_created.append(new_candidate)

    return candidates_created


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
