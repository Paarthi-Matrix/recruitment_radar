from datetime import datetime
from typing import List, Optional

import uuid
from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile
from io import BytesIO
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer
from starlette.middleware.cors import CORSMiddleware

from models.candidate import Candidate, CandidateFactor, CandidateStatus
from models.schema import CandidateCreate, CandidateSchema, SearchCandidateRequest, CandidateCreateResponse, \
    UpdateCandidateRequest

from starlette.responses import StreamingResponse

from db import get_db
import uvicorn
import pandas as pd

from constant.app_constant import CANDIDATE_FIELDS
from models.company import CompanyFactor, Company
from models.factor import Factor
from models.summary import Summary
from utils.jwt_handler import get_current_company_id
from utils.dependencies import require_role, get_current_user

from routes import company, user, factor, summary
from utils.jwt_handler import verify_access_token
from predict.scripts.predict import inference

app = FastAPI()
security = HTTPBearer()
app.include_router(company.router, prefix="/companies", tags=["Companies"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(factor.router, prefix="/factor", tags=["Factors"])
app.include_router(summary.router, prefix="/summary", tags=["Summary"])

token_auth_scheme = HTTPBearer()


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Add your frontend URLs here
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Your authentication dependency
def require_jwt_token(token: str = Depends(token_auth_scheme)):
    # Decode and validate the JWT token here
    # Raise an exception if invalid
    return token


# Custom OpenAPI for JWT Authentication in Swagger
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Your API Title",
        version="1.0.0",
        description="API using JWT Authentication",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.post("/candidates/", dependencies=[Depends(verify_access_token)])
def create_candidate(candidate: CandidateCreate, db: Session = Depends(get_db)):
    try:
        if candidate.email:
            db_candidate = db.query(Candidate).filter(Candidate.email.ilike(candidate.email)).first()
            if db_candidate:
                raise HTTPException(status_code=400, detail="Candidate with this email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while checking for existing candidates")

    # Determine the candidate status
    candidate_status = candidate.status
    if candidate_status not in [status.value for status in CandidateStatus]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status value. Allowed values are: {[status.value for status in CandidateStatus]}"
        )

    new_candidate = Candidate(
        name=candidate.name,
        email=candidate.email,
        location=candidate.location,
        current_role=candidate.current_role,
        experience_years=candidate.experience_years,
        target_role=candidate.target_role,
        target_industry=candidate.target_industry,
        status=candidate_status,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)

    return {"message": "Candidate created successfully", "candidate_id": new_candidate.candidate_id}


@app.get("/candidates", response_model=List[CandidateSchema], dependencies=[Depends(require_role(["Admin"]))])
def get_candidates(
        name: Optional[str] = Query(None, description="Name or partial name of the candidate to search for"),
        page: int = Query(1, ge=1, description="Page number (must be 1 or greater)"),
        size: int = Query(10, ge=1, le=100, description="Number of candidates per page (1-100)"),
        db: Session = Depends(get_db),
):
    """
    Retrieve all candidates with pagination, or search for candidates by name.

    Args:
        name (str, optional): The name or partial name of the candidate to search for.
        page (int): The current page number.
        size (int): The number of candidates per page.
        db (Session): The database session dependency.

    Returns:
        List[CandidateSchema]: A list of candidates matching the search criteria or all candidates.
    """
    query = db.query(Candidate)

    if name:
        query = query.filter(Candidate.name.ilike(f"%{name}%"))

    offset = (page - 1) * size
    candidates = query.offset(offset).limit(size).all()

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

    # Save changes to the database
    db.commit()
    db.refresh(candidate)

    return candidate


@app.get("/xlsx")
def get_excel_data(
        token: str = Depends(get_current_company_id),
        db: Session = Depends(get_db),
):
    """
      Endpoint to generate and download an Excel template for candidate data.

      This endpoint retrieves the factors associated with the given company ID,
      combines them with predefined candidate fields, and generates an Excel file
      with these as column headers. The file is returned as a downloadable response.

      Args:
          token (str): The token containing the current company's ID, provided via dependency injection.
          db (Session): Database session provided via dependency injection.

      Returns:
          StreamingResponse: A downloadable Excel file containing the candidate fields
          and company-specific factor names as column headers.

      Raises:
          HTTPException: If no factors are found for the provided company ID.
      """
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


@app.post("/upload-candidates")
def upload_candidates(file: UploadFile, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """
    Endpoint to process Excel file and insert candidates and their factors.
    """
    global result
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported")

    contents = file.file.read()
    df = pd.read_excel(BytesIO(contents))

    CANDIDATE_COLUMNS = [
        "name", "email", "location", "current_role",
        "experience_years", "target_role", "target_industry"
    ]
    FACTOR_COLUMNS = df.columns[len(CANDIDATE_COLUMNS):]
    company_id = current_user.get('company_id')
    company_name = db.query(Company).filter(Company.company_id == company_id).first()
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
    factors_items = (
        db.query(Factor.factor_name, CompanyFactor.weightage)
        .join(CompanyFactor, Factor.factor_id == CompanyFactor.factor_id)
        .filter(CompanyFactor.company_id == company_id, CompanyFactor.is_active == True)
        .all()
    )
    factors = [item[0] for item in factors_items]
    weightages = [item[1] for item in factors_items]
    result = inference(company_name, df, factors, weightages)

    # Parse model's JSON response
    model_response = result.to_dict()
    scores = model_response.get("Expected_Joining_Score", {})
    summaries = model_response.get("Summary", {})

    for idx, candidate in enumerate(candidates_created):
        candidate_id = candidate.candidate_id
        raw_score = scores.get(idx, 0)
        percentage_score = round((raw_score / 1000) * 100, 1)
        summary_text = summaries.get(idx, "")

        new_summary = Summary(
            prediction_id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            probability_percentage=percentage_score,
            probability_summary=summary_text,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_summary)

    db.commit()

    for candidate in candidates_created:
        candidate.status = CandidateStatus.Reviewed.value
        candidate.updated_at = datetime.utcnow()
        db.add(candidate)

    db.commit()
    return {"Operation success"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
