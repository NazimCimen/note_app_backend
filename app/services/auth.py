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
    """
    
    @staticmethod
    async def verify_supabase_token(token: str) -> dict:
        """
        Verify token using Supabase API
        
        Args:
            token: JWT token string from Supabase
            
        Returns:
            dict: User information from Supabase
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # Use Supabase API to verify token
            headers = {
                "Authorization": f"Bearer {token}",
                "apikey": settings.supabase_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.supabase_url}/auth/v1/user",
                    headers=headers
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    return user_data
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired token",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                    
        except httpx.RequestError as e:
            logger.error(f"Supabase API request failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication service unavailable",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    async def get_user_id_from_token(token: str) -> UUID:
        """
        Extract user ID from Supabase token
        
        Args:
            token: JWT token string from Supabase
            
        Returns:
            UUID: User ID from Supabase
        """
        user_data = await AuthService.verify_supabase_token(token)
        user_id_str = user_data.get("id")
        if user_id_str:
            return UUID(user_id_str)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: user ID not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
