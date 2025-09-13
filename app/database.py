from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from sqlalchemy import event
from app.config import settings

# Create shared Base for all models
Base = declarative_base()

def get_database_url():
    """
    Convert DATABASE_URL to asyncpg format for Supabase
    """
    url = settings.database_url
    
    # Convert postgresql:// to postgresql+asyncpg://
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Remove pgbouncer parameter if present
    if "?pgbouncer=true" in url:
        url = url.replace("?pgbouncer=true", "")
    if "&pgbouncer=true" in url:
        url = url.replace("&pgbouncer=true", "")
    
    return url

# Create async engine with maximum PgBouncer compatibility
engine = create_async_engine(
    get_database_url(),
    echo=False,
    future=True,
    poolclass=NullPool,  # No connection pooling - let PgBouncer handle it
    connect_args={
        "statement_cache_size": 0,  # Disable prepared statements
        "command_timeout": 60,
        "server_settings": {
            "application_name": "notes_app_backend",
            "jit": "off",  # Disable JIT compilation for better PgBouncer compatibility
        }
    }
)

# Event listener removed - not needed with NullPool and disabled prepared statements

# Create async session maker
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=True,
    autocommit=False
)

async def get_db():
    """
    Dependency to get database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()