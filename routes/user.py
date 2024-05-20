from fastapi import APIRouter
from models.user_validation import User
from services.user import User

router = APIRouter()


@router.get('/user')
def user(username: str, email: str):
    created_user = User.create_user(username, email)
    return created_user

