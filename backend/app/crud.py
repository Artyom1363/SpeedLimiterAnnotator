# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas

def get_video(db: Session, video_id: int):
    return db.query(models.Video).filter(models.Video.id == video_id).first()

def get_videos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Video).offset(skip).limit(limit).all()

def create_video(db: Session, video: schemas.VideoCreate):
    db_video = models.Video(filename=video.filename, file_metadata=video.file_metadata)  # Renamed
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

def delete_video(db: Session, video_id: int):
    db_video = get_video(db, video_id)
    if db_video:
        db.delete(db_video)
        db.commit()
    return db_video

