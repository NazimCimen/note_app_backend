import jwt
from fastapi import HTTPException, status
from app.config import settings
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


class AuthService:
    """
    Service for handling JWT authentication with Supabase
    
    This service validates JWT tokens using LOCAL verification (FAST):
    - Validates tokens locally without API calls
    - Much faster than Supabase API verification
    - Still secure with proper JWT validation
    """
    
    @staticmethod
    async def verify_supabase_token_local(token: str) -> dict:
        """
        Verifies JWT token LOCALLY (FAST METHOD)
        
        This method is much faster than API calls:
        - Validates JWT token locally using secret key
        - No network requests to Supabase
        - 10-100x faster than API verification
        
        Args:
            token: JWT token string from Supabase
            
        Returns:
            dict: User information from JWT payload
            
        Raises:
            HTTPException: If token is invalid, expired or malformed
        """
        try:
            # Verify token locally using Supabase JWT secret
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                options={"verify_exp": True, "verify_aud": False}
            )
            
            logger.info(f"JWT token successfully verified locally for user: {payload.get('sub', 'unknown')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Unexpected error during local token verification: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token verification failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    async def get_user_id_from_token(token: str) -> UUID:
        """
        Extracts user ID from JWT token using LOCAL verification (FAST)
        
        Args:
            token: JWT token string
            
        Returns:
            UUID: User's unique identifier
            
        Raises:
            HTTPException: If token is invalid or user ID not found
        """
        # Use LOCAL verification for speed
        user_data = await AuthService.verify_supabase_token_local(token)
        
        # User ID is found in the "sub" field of JWT payload
        user_id_str = user_data.get("sub")
        
        if not user_id_str:
            logger.error("JWT payload missing 'sub' field")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user ID not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            user_uuid = UUID(user_id_str)
            logger.info(f"Successfully extracted user ID from JWT: {user_uuid}")
            return user_uuid
        except ValueError:
            logger.error(f"Invalid UUID format from JWT: {user_id_str}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID format in token",
                headers={"WWW-Authenticate": "Bearer"},
            )
