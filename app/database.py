from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Create the declarative base
Base = declarative_base()

# Async engine with Supabase PostgreSQL
# Convert postgresql:// to postgresql+asyncpg:// for asyncpg driver
database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(
    database_url,
    echo=settings.debug,
    poolclass=NullPool,   # No connection pooling (Vercel-safe)
    connect_args={
        "server_settings": {
            "jit": "off",
        },
        "command_timeout": 30,
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
    Database session dependency
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database (Supabase tables already exist)
    """
    try:
        pass
    except Exception:
        raise


async def close_db():
    """
    Close database connections
    """
    try:
        await engine.dispose()
    except Exception:
        raise
