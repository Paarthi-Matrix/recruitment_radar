from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from models.company import Company, CompanyFactor
from models.factor import Factor
from schemas.company import CompanyCreate, CompanyOut, AddCompanyFactorsRequest
from services.company import create_company, get_all_companies

router = APIRouter()

@router.post("/", response_model=CompanyOut)
def create_new_company(company: CompanyCreate, db: Session = Depends(get_db)):
    return create_company(db, company)

@router.get("/", response_model=List[CompanyOut], summary="Get all companies")
def list_companies(db: Session = Depends(get_db)):
    """
    Fetch all companies from the database.
    """
    return get_all_companies(db)


@router.post("/companies/{company_id}/factors")
def add_factors_to_company(
    request: AddCompanyFactorsRequest,
    db: Session = Depends(get_db)
):
    # Validate if the company exists
    company = db.query(Company).filter_by(company_id=str(request.company_id)).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Validate if each factor exists
    for factor_data in request.factors:
        factor = db.query(Factor).filter_by(factor_id=str(factor_data.factor_id)).first()
        if not factor:
            raise HTTPException(
                status_code=404,
                detail=f"Factor with ID {factor_data.factor_id} not found"
            )

    # Add factors with weightages to the company
    for factor_data in request.factors:
        existing_entry = (
            db.query(CompanyFactor)
            .filter_by(company_id=str(request.company_id), factor_id=str(factor_data.factor_id))
            .first()
        )
        if existing_entry:
            # Update existing entry
            existing_entry.weightage = factor_data.weightage
            existing_entry.is_active = True
        else:
            # Create a new entry
            company_factor = CompanyFactor(
                company_id=str(request.company_id),
                factor_id=str(factor_data.factor_id),
                weightage=factor_data.weightage,
                is_active=True
            )
            db.add(company_factor)

    db.commit()
    return {"message": "Factors successfully added/updated for the company"}

