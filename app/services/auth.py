import jwt
import httpx
from fastapi import HTTPException, status
from app.config import settings
from typing import Optional
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class AuthService:
    """
    Service for handling JWT authentication with Supabase
    
    This service validates JWT tokens using Supabase API (Production-ready):
    - Independent of JWT secret changes
    - Validates tokens directly with Supabase API
    - Reliable and maintainable authentication
    """
    
    @staticmethod
    async def verify_supabase_token(token: str) -> dict:
        """
        Verifies JWT token with Supabase API
        
        This method is independent of JWT secrets:
        - Sends token to Supabase API for verification
        - Returns user information from Supabase
        - Works even if JWT secret changes
        
        Args:
            token: JWT token string from Supabase
            
        Returns:
            dict: User information from Supabase API
            
        Raises:
            HTTPException: If token is invalid, expired or malformed
        """
        try:
            # Verify token with Supabase API
            headers = {
                "Authorization": f"Bearer {token}",
                "apikey": settings.supabase_key,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                # Request to Supabase user endpoint
                response = await client.get(
                    f"{settings.supabase_url}/auth/v1/user",
                    headers=headers
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    logger.info(f"JWT token successfully verified via Supabase API for user: {user_data.get('id', 'unknown')}")
                    return user_data
                else:
                    logger.warning(f"Supabase API returned {response.status_code}: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token verification failed with Supabase",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            
        except httpx.RequestError as e:
            logger.error(f"Supabase API request failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication service temporarily unavailable",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token verification failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    async def get_user_id_from_token(token: str) -> UUID:
        """
        Extracts user ID from JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            UUID: User's unique identifier
            
        Raises:
            HTTPException: If token is invalid or user ID not found
        """
        user_data = await AuthService.verify_supabase_token(token)
        
        # User ID is found in the "id" field of Supabase API response
        user_id_str = user_data.get("id")
        
        if not user_id_str:
            logger.error("Supabase API response missing 'id' field")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid response: user ID not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            user_uuid = UUID(user_id_str)
            logger.info(f"Successfully extracted user ID from Supabase API: {user_uuid}")
            return user_uuid
        except ValueError:
            logger.error(f"Invalid UUID format from Supabase: {user_id_str}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID format from Supabase",
                headers={"WWW-Authenticate": "Bearer"},
            )
