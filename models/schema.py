from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from typing import Optional

from .user import CandidateStatus


class UserRole(str, Enum):
    admin = "Admin"
    recruiter = "Recruiter"


class UserCreate(BaseModel):
    name: str
    email: str
    role: UserRole
    password_hash: str

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
    status: CandidateStatus
