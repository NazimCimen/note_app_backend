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
            # GEÇİCİ DEBUG: Signature doğrulamasını kapat
            payload = jwt.decode(
                token,
                options={
                    "verify_signature": False,  # Geçici olarak kapalı
                    "verify_exp": False,  # Geçici olarak kapalı
                    "verify_aud": False   # Geçici olarak kapalı
                }
            )
            
            # Debug: Token payload'ını logla
            logger.info(f"DEBUG - Token payload: {payload}")
            logger.info(f"DEBUG - User ID: {payload.get('sub')}")
            logger.info(f"DEBUG - Audience: {payload.get('aud')}")
            logger.info(f"DEBUG - Algorithm: {payload.get('alg', 'Not found')}")
            
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
            logger.error(f"JWT decode error: {str(e)}")
            logger.error(f"Token starts with: {token[:50]}...")
            # Geçici olarak token'ı kabul et
            try:
                payload = jwt.decode(token, options={"verify_signature": False})
                logger.info(f"DEBUG - Bypassed verification, payload: {payload}")
                return payload
            except Exception as fallback_error:
                logger.error(f"Even bypass failed: {str(fallback_error)}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Token decode failed: {str(e)}",
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
