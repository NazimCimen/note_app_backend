from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
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
    logger.info("Using Supabase managed database - no table creation needed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Notes App Backend...")


# Create FastAPI instance
app = FastAPI(
    title=settings.project_name,
    description="A professional note-taking application backend built with FastAPI and Supabase",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware to allow frontend connections
# Use specific origins in production for security
allowed_origins = [
    "http://localhost:3000",  # Flutter web development
    "http://127.0.0.1:3000",
    "https://your-flutter-app.vercel.app",  # Production Flutter web
    "https://your-flutter-app.netlify.app",
    # Mobile apps don't need origins, only web apps
]

# Allow all origins in development, restrict in production
if settings.debug:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
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

# For Vercel deployment
handler = app

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
