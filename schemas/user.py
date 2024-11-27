from enum import Enum

from pydantic import BaseModel

class UserBase(BaseModel):
    name: str
    email: str
    role: str

class UserRole(str, Enum):
    admin = "admin"
    recruiter = "recruiter"


class UserCreate(BaseModel):
    name: str
    email: str
    role: UserRole
    password: str
    company_id: str

    class Config:
        orm_mode = True

class UserOut(UserBase):
    user_id: str

    class Config:
        orm_mode = True

