from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import create_tables
from app.routers import notes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager - handles startup and shutdown events
    """
    # Startup
    logger.info("Starting up Notes App Backend...")
    


    # Create database tables
    try:
        await create_tables()  # Uncommented to enable database
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        # Don't raise error, continue without DB for testing
    
    yield
    
    # Shutdown
    logger.info("Shutting down Notes App Backend...")


# Create FastAPI instance
app = FastAPI(
    title=settings.project_name,
    description="A professional note-taking application backend built with FastAPI and Supabase",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(notes.router, prefix=settings.api_v1_str)

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint that returns API information
    """
    return {
        "message": f"Welcome to {settings.project_name}!",
        "status": "running",
        "version": "1.0.0",
        "docs_url": "/docs",
        "api_v1": settings.api_v1_str
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is working
    """
    return {
        "status": "healthy",
        "message": "API is running successfully",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
