from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from db import get_db
from models.company import Company
from models.schema import UserLogin
from models.user import User
from schemas.user import UserCreate

router = APIRouter()

# Password hashing utility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash the password using bcrypt."""
    return pwd_context.hash(password)


@router.post("/create/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    print('model: ', User)
    # Check if the email is already registered
    db_user = db.query(User).filter(User.email==user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if the company exists
    db_company = db.query(Company).filter(Company.company_id==user.company_id).first()
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Create a new user
    new_user = User(
        name=user.name,
        email=user.email,
        role=user.role,
        password_hash=hash_password(user.password),
        company_id=user.company_id,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()  # Rollback the transaction in case of an error
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

    return {
        "status": "success",
        "data": {
            "message": "User successfully created",
            "user_id": new_user.user_id,
        },
    }


@router.post("/login/")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="Invalid email or password")

    if not pwd_context.verify(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"message": "Login successful", "email": db_user.email}

