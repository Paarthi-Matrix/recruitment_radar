from sqlalchemy.orm import Session
from models.company import Company
from schemas.company import CompanyCreate

def create_company(db: Session, company: CompanyCreate) -> Company:
    db_company = Company(**company.model_dump())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def get_all_companies(db: Session):
    """
    Fetch all companies from the database.
    """
    return db.query(Company).all()

