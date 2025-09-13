from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.config import settings

# Create shared Base for all models
Base = declarative_base()

# Create async database engine
engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=True,  # Set to False in production
    future=True,
    # Fix for pgbouncer transaction mode - disable prepared statements
    connect_args={
        "statement_cache_size": 0,
    }
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


async def create_tables():
    """
    Create all tables in the database
    """
    # Import models to ensure they are registered with Base
    from app.models.note import Note
    from app.models.user import User
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
