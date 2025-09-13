from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # Supabase Configuration
    supabase_url: str
    supabase_key: str
    supabase_jwt_secret: str
    
    # Database Configuration
    database_url: str
    
    # JWT Configuration (for future use or custom JWT implementation)
    jwt_secret_key: str = "fallback-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # API Configuration
    api_v1_str: str = "/api/v1"
    project_name: str = "Notes App Backend"
    
    # Environment
    debug: bool = True
    
    @property
    def is_development(self) -> bool:
        return self.debug
    
    @property
    def is_production(self) -> bool:
        return not self.debug
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()