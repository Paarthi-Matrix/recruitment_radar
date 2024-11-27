from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from schemas.factor import FactorCreate, FactorResponse
from services.factor import create_factor, get_all_factors

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

