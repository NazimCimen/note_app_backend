from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.config import settings

# Create shared Base for all models
Base = declarative_base()

# Create async database engine for Supabase with PgBouncer
def get_database_url():
    """
    Convert DATABASE_URL to asyncpg format and remove pgbouncer parameter
    (pgbouncer compatibility is handled via connect_args)
    """
    url = settings.database_url
    
    # Convert postgresql:// to postgresql+asyncpg://
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Remove pgbouncer parameter if present (AsyncPG doesn't recognize it)
    if "?pgbouncer=true" in url:
        url = url.replace("?pgbouncer=true", "")
    if "&pgbouncer=true" in url:
        url = url.replace("&pgbouncer=true", "")
    
    return url

engine = create_async_engine(
    get_database_url(),
    echo=False,  # Disabled in production
    future=True,
    # Serverless-optimized settings (Vercel compatible)
    connect_args={
        "statement_cache_size": 0,  # No prepared statements for PgBouncer
        "prepared_statement_cache_size": 0,
        "command_timeout": 60,  # Timeout for long queries
    },
    # Serverless connection settings - no persistent connections
    pool_size=1,        # Single connection per function
    max_overflow=0,     # No overflow in serverless
    pool_pre_ping=False, # No need to ping in serverless
    pool_recycle=300,   # Recycle connections after 5 minutes
    pool_timeout=30,    # Connection timeout
)

# Create async session maker
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


async def get_db():
    """
    Dependency to get database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


