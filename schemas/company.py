from uuid import UUID

from pydantic import BaseModel
from typing import List, Optional

from schemas.user import UserOut


class CompanyBase(BaseModel):
    company_name: str
    company_location: str
    company_email: str

class CompanyCreate(CompanyBase):
    pass

class CompanyOut(CompanyBase):
    company_id: UUID
    users: List[UserOut] = []

    class Config:
        orm_mode = True
#
# class CompanyResponse(BaseModel):
#     company_id: str
#     company_name: str
#     company_location: str
#     company_email: str
#     users: Optional[List[UserResponse]] = []  # List of users (optional)
#
#     class Config:
#         orm_mode = True


class FactorWeightage(BaseModel):
    factor_id: UUID
    weightage: float

class AddCompanyFactorsRequest(BaseModel):
    company_id: UUID
    factors: List[FactorWeightage]