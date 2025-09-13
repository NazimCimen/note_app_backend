from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth import AuthService
from typing import Optional
from uuid import UUID

# Security scheme for Bearer token
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UUID:
    """
    Dependency to get current authenticated user from JWT token
    
    Args:
        credentials: HTTP authorization credentials containing Bearer token
        
    Returns:
        UUID: User ID of the authenticated user
        
    Raises:
        HTTPException: If token is missing or invalid
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    user_id = AuthService.get_user_id_from_token(token)
    return user_id


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[UUID]:
    """
    Optional dependency to get current user (for endpoints that work with or without auth)
    
    Args:
        credentials: Optional HTTP authorization credentials
        
    Returns:
        Optional[UUID]: User ID if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user_id = AuthService.get_user_id_from_token(token)
        return user_id
    except HTTPException:
        return None
