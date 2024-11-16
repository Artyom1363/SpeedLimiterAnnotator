from fastapi import FastAPI
from app.routers import videos
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Video Annotation Backend")

app.include_router(videos.router, prefix="/videos", tags=["Videos"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Video Annotation Backend API"}
