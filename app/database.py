from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Create the declarative base
Base = declarative_base()

# Create async engine with Supabase PostgreSQL
# Using connection pooling URL for better performance on Vercel
# Convert postgresql:// to postgresql+asyncpg:// for asyncpg driver
database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(
    database_url,
    echo=settings.debug,  # Log SQL queries in debug mode
    poolclass=NullPool,   # Disable connection pooling for serverless (Vercel)
    pool_pre_ping=True,   # Verify connections before use
    pool_recycle=300,     # Recycle connections every 5 minutes
    connect_args={
        "server_settings": {
            "jit": "off",  # Disable JIT for faster connection
        }
    }
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncSession:
    """
    Dependency to get database session
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database - For Supabase, tables already exist
    
    Note: Tables are managed via Supabase Dashboard
    This function is kept for compatibility but doesn't create tables
    """
    try:
        logger.info("Using existing Supabase tables - no initialization needed")
        # Tables already exist in Supabase, no need to create them
        pass
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise


async def close_db():
    """
    Close database connections
    """
    try:
        await engine.dispose()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
        raise
