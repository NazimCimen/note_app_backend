import jwt
from fastapi import HTTPException, status
from app.config import settings
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class AuthService:
    """
    JWT authentication service with Supabase
    Uses local token verification for optimal performance
    """
    
    @staticmethod
    async def verify_supabase_token_local(token: str) -> dict:
        """
        Local JWT token verification (fast method)
        """
        try:
            # Local JWT verification
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                options={"verify_exp": True, "verify_aud": False}
            )
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token verification failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    async def get_user_id_from_token(token: str) -> UUID:
        """
        Extract user ID from JWT token
        """
        user_data = await AuthService.verify_supabase_token_local(token)
        user_id_str = user_data.get("sub")
        
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user ID not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            user_uuid = UUID(user_id_str)
            return user_uuid
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID format in token",
                headers={"WWW-Authenticate": "Bearer"},
            )
