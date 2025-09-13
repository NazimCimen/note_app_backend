import jwt
from fastapi import HTTPException, status
from app.config import settings
from typing import Optional
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class AuthService:
    """
    Service for handling JWT authentication with Supabase
    
    Bu servis JWT token'ları lokal olarak doğrular:
    1. HS256 algoritması kullanır (Supabase standardı)
    2. SUPABASE_JWT_SECRET ile doğrular
    3. Hızlı ve güvenilir
    """
    
    @staticmethod
    async def verify_supabase_token(token: str) -> dict:
        """
        JWT token'ı HS256 ile doğrular (Supabase standard sistemi)
        
        Args:
            token: Supabase'den gelen JWT token string
            
        Returns:
            dict: Token payload'ı (kullanıcı bilgileri içerir)
            
        Raises:
            HTTPException: Token geçersiz, süresi dolmuş veya bozuksa
        """
        try:
            # JWT token'ı Supabase JWT secret ile decode et
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,  # .env dosyasındaki secret
                algorithms=["HS256"],  # Supabase hâlâ HS256 kullanıyor
                audience="authenticated",
                options={
                    "verify_signature": True,
                    "verify_exp": True,  # Expiry time kontrol et
                    "verify_aud": True   # Audience kontrol et
                }
            )
            
            # Token payload'ını log'la (debug için)
            logger.info(f"JWT token successfully verified for user: {payload.get('sub', 'unknown')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired. Please login again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidAudienceError:
            logger.warning("JWT token has invalid audience")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token audience",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format or signature",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Unexpected error during JWT verification: {str(e)}")
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
        payload = await AuthService.verify_supabase_token(token)
        
        # JWT standartında user ID "sub" (subject) field'ında bulunur
        user_id_str = payload.get("sub")
        
        if not user_id_str:
            logger.error("JWT token payload missing 'sub' field")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user ID not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            user_uuid = UUID(user_id_str)
            logger.info(f"Successfully extracted user ID: {user_uuid}")
            return user_uuid
        except ValueError:
            logger.error(f"Invalid UUID format in token: {user_id_str}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID format in token",
                headers={"WWW-Authenticate": "Bearer"},
            )
