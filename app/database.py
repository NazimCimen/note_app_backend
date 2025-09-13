from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.config import settings

# Create shared Base for all models
Base = declarative_base()

# Create async database engine with PgBouncer compatibility
engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=False,  # Disabled in production for better performance
    future=True,
    # PgBouncer compatibility settings
    connect_args={
        "statement_cache_size": 0,  # Disable prepared statements for PgBouncer
        "prepared_statement_cache_size": 0,  # Additional cache disable
        "server_settings": {
            "application_name": "notes_app_backend",
            "jit": "off",  # Disable JIT for better PgBouncer compatibility
        }
    },
    # Pool settings for better connection management
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections every hour
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


