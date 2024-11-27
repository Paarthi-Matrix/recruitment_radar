import logging

from sqlalchemy.orm import Session

from models.factor import Factor
from schemas.factor import FactorCreate

logger = logging.getLogger("log")



def create_factor(db: Session, factor: FactorCreate) -> Factor:
    db_company = Factor(**factor.model_dump())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def get_all_factors(db: Session):
    """
    Fetch all factors from the database.
    """
    return db.query(Factor).all()

