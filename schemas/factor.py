from uuid import UUID

from pydantic import BaseModel


class FactorBase(BaseModel):
    factor_name: str
    factor_description: str


class FactorCreate(FactorBase):
    pass

class FactorResponse(FactorBase):
    factor_id: UUID

    class Config:
        orm_mode = True
