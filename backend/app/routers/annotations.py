# Path: backend/app/routers/annotations.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List
from .. import crud, schemas, models
from ..database import get_db
from ..dependencies import get_current_user, get_video_or_404

router = APIRouter(
    prefix="/api/annotations",
    tags=["annotations"]
)

@router.post("/{video_id}/start", response_model=schemas.LockResponse)
async def start_annotation(
    video_id: str,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start annotating a video and lock it"""
    video = await get_video_or_404(video_id, db)
    
    try:
        video = await crud.lock_video(db, video_id, current_user.id)
    except HTTPException as e:
        if e.status_code == status.HTTP_409_CONFLICT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Video is already locked by another user"
            )
        raise e
    
    return {
        "status": "started",
        "video_id": video.id,
        "user_id": current_user.id,
        "locked_by": video.locked_by,
        "lock_time": video.lock_time
    }

@router.post("/{video_id}/commit", response_model=schemas.AnnotationResponse)
async def commit_annotations(
    video_id: str,
    annotations: List[schemas.AnnotationCreate],
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Commit annotations for a video"""
    video = await get_video_or_404(video_id, db)
    
    if video.locked_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to annotate this video"
        )
    
    committed_annotations = await crud.create_annotations_bulk(
        db,
        video_id,
        current_user.id,
        [ann.dict() for ann in annotations]
    )
    
    return {
        "status": "committed",
        "video_id": video_id,
        "annotations": annotations
    }

@router.post("/{video_id}/unlock", response_model=schemas.UnlockResponse)
async def unlock_video(
    video_id: str,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unlock a video after completing annotation"""
    video = await get_video_or_404(video_id, db)
    
    try:
        video = await crud.unlock_video(db, video_id, current_user.id)
    except HTTPException as e:
        if e.status_code == status.HTTP_403_FORBIDDEN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to unlock this video"
            )
        raise e
    
    return {
        "status": "unlocked",
        "video_id": video.id
    }

@router.post("/{video_id}/shift_timestamp", response_model=schemas.TimestampShiftResponse)
async def shift_video_timestamp(
    video_id: str,
    timestamp_offset: float,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Shift video timestamps by a given offset"""
    video = await get_video_or_404(video_id, db)
    
    if video.locked_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this video"
        )
    
    await crud.update_video_timestamp_offset(db, video_id, timestamp_offset)
    
    return {
        "status": "success",
        "message": "Video timestamps shifted successfully"
    }

@router.post("/{video_id}/shift_button_timestamp", response_model=schemas.TimestampShiftResponse)
async def shift_button_timestamp(
    video_id: str,
    timestamp_offset: float,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Shift button data timestamps by a given offset"""
    video = await get_video_or_404(video_id, db)
    
    if video.locked_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this video"
        )
    
    await crud.update_button_data_timestamp_offset(db, video_id, timestamp_offset)
    
    return {
        "status": "success",
        "message": "Button data timestamps shifted successfully"
    }