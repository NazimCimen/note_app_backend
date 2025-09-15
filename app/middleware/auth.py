from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth import AuthService
from typing import Optional
from uuid import UUID

# Security scheme for Bearer token
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UUID:
    """
    Get current authenticated user from JWT token
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    user_id = await AuthService.get_user_id_from_token(token)
    return user_id


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[UUID]:
    """
    Optional user authentication (for endpoints that work with or without auth)
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user_id = await AuthService.get_user_id_from_token(token)
        return user_id
    except HTTPException:
        return None
