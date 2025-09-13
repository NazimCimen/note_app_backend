import jwt
from jwt import PyJWKClient
from fastapi import HTTPException, status
from app.config import settings
from typing import Optional
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class AuthService:
    """
    Service for handling JWT authentication with Supabase
    
    Bu servis JWT token'ları JWKS ile doğrular (Supabase'in yeni sistemi):
    1. RS256 algoritması kullanır (artık HS256 değil)
    2. JWKS URL'den public key alır
    3. Supabase'in güncel güvenlik standardına uygun
    """
    
    @staticmethod
    async def verify_supabase_token(token: str) -> dict:
        """
        JWT token'ı JWKS ile doğrular (Supabase'in yeni sistemi)
        
        Args:
            token: Supabase'den gelen JWT token string
            
        Returns:
            dict: Token payload'ı (kullanıcı bilgileri içerir)
            
        Raises:
            HTTPException: Token geçersiz, süresi dolmuş veya bozuksa
        """
        try:
            # JWKS URL - Supabase'in public key'lerini içerir
            jwks_url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
            
            # JWKS client oluştur
            jwks_client = PyJWKClient(jwks_url)
            
            # Token'dan signing key'i al
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            
            # Token'ı RS256 ile doğrula (artık HS256 değil!)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],  # Supabase artık RS256 kullanıyor
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
