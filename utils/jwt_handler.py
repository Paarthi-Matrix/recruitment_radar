from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from config import settings

from models.user import UserRole


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data (dict): The payload data.
        expires_delta (timedelta): Optional expiry time for the token.

    Returns:
        str: The generated JWT token.
    """
    to_encode = data.copy()
    for key, value in to_encode.items():
        if isinstance(value, UserRole):
            to_encode[key] = str(value)

    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_access_token(token: str) -> dict:
    """
    Verify and decode a JWT token.

    Args:
        token (str): The JWT token.

    Returns:
        dict: The decoded payload if valid.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get the current authenticated user from the JWT token.

    Args:
        token (str): The JWT token.

    Returns:
        dict: The user information.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return payload


def require_role(allowed_roles: list):
    """
    Dependency to enforce role-based access control.

    Args:
        allowed_roles (list): List of roles allowed to access the endpoint.

    Returns:
        Callable: A dependency callable.
    """

    def role_checker(user=Depends(get_current_user)):
        if user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: insufficient permissions",
            )
        return user

    return role_checker