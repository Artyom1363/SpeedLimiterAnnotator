# app/routers/videos.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import shutil
import os

from app import crud, schemas
from app.database import SessionLocal

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.Video)
def upload_video(video: schemas.VideoCreate, db: Session = Depends(get_db)):
    db_video = crud.create_video(db, video)
    return db_video

@router.get("/", response_model=List[schemas.Video])
def read_videos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    videos = crud.get_videos(db, skip=skip, limit=limit)
    return videos

@router.get("/{video_id}", response_model=schemas.Video)
def read_video(video_id: int, db: Session = Depends(get_db)):
    db_video = crud.get_video(db, video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return db_video

@router.delete("/{video_id}", response_model=schemas.Video)
def delete_video(video_id: int, db: Session = Depends(get_db)):
    db_video = crud.delete_video(db, video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return db_video

@router.post("/upload-file/", response_model=schemas.Video)
def upload_file(filename: str, file_metadata: str = None, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Save the file locally or to a storage service
    upload_dir = "uploads/"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    video_create = schemas.VideoCreate(filename=file.filename, file_metadata=file_metadata)  # Renamed
    db_video = crud.create_video(db, video_create)
    return db_video

