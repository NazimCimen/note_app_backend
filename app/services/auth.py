from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.config import settings
from typing import Optional
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class AuthService:
    """
    Service for handling JWT authentication with Supabase
    """
    
    @staticmethod
    def verify_jwt_token(token: str) -> dict:
        """
        Verify and decode JWT token from Supabase
        
        Args:
            token: JWT token string
            
        Returns:
            dict: Decoded token payload containing user information
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # Decode JWT token - skip signature verification for now
            # TODO: Implement proper Supabase JWT verification
            payload = jwt.decode(
                token,
                options={"verify_signature": False, "verify_aud": False}
            )
            
            # Extract user ID from token
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user ID",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return payload
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def get_user_id_from_token(token: str) -> UUID:
        """
        Extract user ID from JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            UUID: User ID from token (converted to UUID)
        """
        payload = AuthService.verify_jwt_token(token)
        user_id_str = payload.get("sub")
        if user_id_str:
            # Convert string user ID to UUID to match database schema
            return UUID(user_id_str)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: user ID not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
