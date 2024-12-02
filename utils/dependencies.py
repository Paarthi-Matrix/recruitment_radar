from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .jwt_handler import verify_access_token

oauth2_scheme = HTTPBearer()


def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    """
    Get the current authenticated user from the JWT token.

    Args:
        token (HTTPAuthorizationCredentials): The authorization credentials object.

    Returns:
        dict: The user information.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    # Extract the actual token string
    token_str = token.credentials

    # Verify the token
    payload = verify_access_token(token_str)
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
