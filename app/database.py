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
    Convert DATABASE_URL to asyncpg format and ensure pgbouncer parameter is present
    """
    url = settings.database_url
    
    # Convert postgresql:// to postgresql+asyncpg://
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Ensure pgbouncer=true parameter is present
    if "pgbouncer=true" not in url:
        separator = "&" if "?" in url else "?"
        url += f"{separator}pgbouncer=true"
    
    return url

engine = create_async_engine(
    get_database_url(),
    echo=False,  # Disabled in production
    future=True,
    # Minimal settings - let pgbouncer handle connection management
    pool_size=1,
    max_overflow=0,
    pool_pre_ping=False,  # Let pgbouncer handle this
    pool_recycle=-1,      # No connection recycling
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


