# Path: backend/app/routers/videos.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from typing import List
import uuid

router = APIRouter()

@router.post("/upload_video")
async def upload_video(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    video_id = str(uuid.uuid4())
    # Здесь будет логика загрузки видео
    return {"video_id": video_id, "message": "Video uploaded successfully"}

@router.get("/next_unannotated")
async def get_next_unannotated(
    db: AsyncSession = Depends(get_db)
):
    # Здесь будет логика получения следующего видео
    return {"video_id": "test_id", "status": "unannotated"}