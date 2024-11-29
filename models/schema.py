from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from typing import Optional

from models.models import CandidateStatus


class UserRole(str, Enum):
    admin = "admin"
    recruiter = "recruiter"


class UserCreate(BaseModel):
    name: str
    email: str
    role: UserRole
    password_hash: str
    company_id: str

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class CandidateCreate(BaseModel):
    name: str = Field(..., max_length=255)
    email: Optional[EmailStr] = None
    location: str = Field(..., max_length=100)
    current_role: str = Field(..., max_length=255)
    experience_years: float
    target_role: str = Field(..., max_length=255)
    target_industry: str = Field(..., max_length=100)


class CandidateSchema(BaseModel):
    candidate_id: str
    name: str
    email: Optional[str] = None
    location: str
    current_role: str
    experience_years: float
    target_role: str
    target_industry: str
    status: str

    class Config:
        orm_mode = True


class SearchCandidateRequest(BaseModel):
    name: str


class UpdateCandidateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    current_role: Optional[str] = None
    experience_years: Optional[float] = None
    target_role: Optional[str] = None
    target_industry: Optional[str] = None
    status: Optional[CandidateStatus] = None


class CandidateCreateResponse(BaseModel):
    candidate_id: str
    name: str
    email: str
    location: str
    current_role: str
    experience_years: float
    target_role: str
    target_industry: str
    status: str

    class Config:
        orm_mode = True
