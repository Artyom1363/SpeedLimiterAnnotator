# Path: backend/app/routers/annotations.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List
from .. import crud, schemas, models
from ..database import get_db
from ..dependencies import get_current_user, get_video_or_404, check_video_lock

router = APIRouter(
    prefix="/api/annotations",
    tags=["annotations"]
)

@router.post("/{video_id}/start", response_model=schemas.DataResponse)
async def start_annotation(
    video_id: str,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    video = await get_video_or_404(video_id, db)
    
    # Check if video is already locked
    if video.locked_by and video.locked_by != current_user.id:
        if video.lock_time and (datetime.utcnow() - video.lock_time).total_seconds() < 3600:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Video is already locked by another user"
            )
    
    # Lock the video
    video.locked_by = current_user.id
    video.lock_time = datetime.utcnow()
    video.status = "in_progress"
    await db.commit()
    
    return {
        "status": "started",
        "message": "Annotation started successfully",
        "data": {
            "video_id": video.id,
            "user_id": current_user.id,
            "locked_by": video.locked_by,
            "lock_time": video.lock_time
        }
    }

@router.post("/{video_id}/commit", response_model=schemas.DataResponse)
async def commit_annotations(
    video_id: str,
    annotations: List[schemas.AnnotationCreate],
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    video = await get_video_or_404(video_id, db)
    await check_video_lock(video, current_user)
    
    committed_annotations = []
    for annotation_data in annotations:
        annotation = await crud.create_annotation(
            db, video_id, current_user.id, annotation_data
        )
        committed_annotations.append(annotation)
    
    return {
        "status": "committed",
        "message": "Annotations committed successfully",
        "data": {
            "video_id": video_id,
            "annotations": [
                {
                    "timestamp": ann.timestamp,
                    "speed": ann.speed,
                    "button_state": ann.button_state,
                    "error_detected": ann.error_detected
                }
                for ann in committed_annotations
            ]
        }
    }

@router.post("/{video_id}/unlock", response_model=schemas.StandardResponse)
async def unlock_video(
    video_id: str,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    video = await get_video_or_404(video_id, db)
    await check_video_lock(video, current_user)
    
    video.locked_by = None
    video.lock_time = None
    video.status = "completed"
    await db.commit()
    
    return {
        "status": "success",
        "message": "Video unlocked successfully"
    }

@router.post("/{video_id}/shift_timestamp", response_model=schemas.StandardResponse)
async def shift_video_timestamp(
    video_id: str,
    timestamp_offset: float,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    video = await get_video_or_404(video_id, db)
    await check_video_lock(video, current_user)
    
    # Update video timestamp offset
    await crud.update_video_timestamp_offset(db, video_id, timestamp_offset)
    
    return {
        "status": "success",
        "message": "Video timestamps shifted successfully"
    }

@router.post("/{video_id}/shift_button_timestamp", response_model=schemas.StandardResponse)
async def shift_button_timestamp(
    video_id: str,
    timestamp_offset: float,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    video = await get_video_or_404(video_id, db)
    await check_video_lock(video, current_user)
    
    # Update button data timestamp offset
    await crud.update_button_data_timestamp_offset(db, video_id, timestamp_offset)
    
    return {
        "status": "success",
        "message": "Button data timestamps shifted successfully"
    }