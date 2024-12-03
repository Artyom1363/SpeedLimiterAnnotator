# Path: backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import async_engine, Base
from app.routers import auth, videos, annotations, inference
from app.config import get_settings
import logging
import sys

# Configure logging to use stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create upload directory if it doesn't exist
    import os
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Create tables on startup
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")
    yield
    # Cleanup
    logger.info("Application shutting down")

app = FastAPI(
    title="Speed Limiter Video Annotation API",
    description="API for managing video annotations and speed limit analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(videos.router)
app.include_router(annotations.router)
app.include_router(inference.router)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "server": settings.BACKEND_HOST,
        "port": settings.BACKEND_PORT
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        proxy_headers=True,
        forwarded_allow_ips="*"
    )
