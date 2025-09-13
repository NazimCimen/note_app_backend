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
    
    Bu servis JWT token'ları Supabase API ile doğrular (Production-ready):
    1. JWT secret'a bağımlı değil - secret değişse bile çalışır
    2. Supabase API'ye token gönderir ve doğrulama yapar
    3. Güvenilir ve sürdürülebilir
    """
    
    @staticmethod
    async def verify_supabase_token(token: str) -> dict:
        """
        JWT token'ı Supabase API ile doğrular (Production-ready)
        
        Bu yöntem JWT secret'a bağımlı değildir:
        - Supabase API'ye token'ı gönderir
        - Supabase token'ı doğrular ve kullanıcı bilgilerini döner
        - JWT secret değişse bile çalışır
        
        Args:
            token: Supabase'den gelen JWT token string
            
        Returns:
            dict: Kullanıcı bilgileri (Supabase API'den)
            
        Raises:
            HTTPException: Token geçersiz, süresi dolmuş veya bozuksa
        """
        try:
            # Supabase API ile token doğrulama
            headers = {
                "Authorization": f"Bearer {token}",
                "apikey": settings.supabase_key,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                # Supabase user endpoint'ine istek at
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
        JWT token'dan kullanıcı ID'sini çıkarır
        
        Args:
            token: JWT token string
            
        Returns:
            UUID: Kullanıcının benzersiz ID'si
            
        Raises:
            HTTPException: Token geçersizse veya user ID bulunamazsa
        """
        user_data = await AuthService.verify_supabase_token(token)
        
        # Supabase API response'unda user ID "id" field'ında bulunur
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
