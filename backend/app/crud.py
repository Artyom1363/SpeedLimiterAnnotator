# Path: backend/app/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, text
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from . import models, schemas
from typing import List, Optional, Dict, Any

# User operations
async def get_user(db: AsyncSession, user_id: str) -> Optional[models.User]:
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    result = await db.execute(select(models.User).filter(models.User.email == email))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user_data: schemas.UserCreate, hashed_password: str) -> models.User:
    db_user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# Video operations
async def create_video(
    db: AsyncSession,
    filename: str,
    s3_key: str,
    user_id: str
) -> models.Video:
    db_video = models.Video(
        filename=filename,
        s3_key=s3_key,
        user_id=user_id,
        status="unannotated"
    )
    db.add(db_video)
    await db.commit()
    await db.refresh(db_video)
    return db_video

async def get_video(db: AsyncSession, video_id: str) -> Optional[models.Video]:
    result = await db.execute(
        select(models.Video)
        .options(selectinload(models.Video.speed_data))
        .options(selectinload(models.Video.button_data))
        .filter(models.Video.id == video_id)
    )
    return result.scalar_one_or_none()

async def get_next_unannotated_video(db: AsyncSession) -> Optional[models.Video]:
    """Get the next video that needs annotation"""
    result = await db.execute(
        select(models.Video)
        .filter(models.Video.status == "unannotated")
        .order_by(models.Video.upload_date)
    )
    return result.scalar_one_or_none()


async def create_speed_data_bulk(db: AsyncSession, video_id: str, speed_data: List[dict]) -> List[models.SpeedData]:
    """Parse and create speed data records from CSV"""
    db_speed_data = []
    try:
        for data in speed_data:
            # Преобразование заголовков из CSV
            db_speed_data.append(models.SpeedData(
                video_id=video_id,
                timestamp=float(data['Elapsed time (sec)']), 
                speed=float(data['Speed (km/h)']),
                latitude=float(data['Latitude']),
                longitude=float(data['Longitude']),
                altitude=float(data['Altitude (km)']),
                accuracy=float(data['Accuracy (km)'])
            ))
        
        db.add_all(db_speed_data)
        await db.commit()
        return db_speed_data
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing speed data: {str(e)}"
        )

# Button data operations
async def create_button_data_bulk(db: AsyncSession, video_id: str, button_data: List[dict]) -> List[models.ButtonData]:
    db_button_data = []
    for data in button_data:
        try:
            db_button_data.append(models.ButtonData(
                video_id=video_id,
                timestamp=float(data['timestamp']),
                state=bool(data['state'])
            ))
        except (ValueError, KeyError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid button data format: {str(e)}"
            )
    
    db.add_all(db_button_data)
    await db.commit()
    return db_button_data

# Annotation operations
async def create_annotation(
    db: AsyncSession,
    video_id: str,
    user_id: str,
    annotation_data: schemas.AnnotationCreate
) -> models.Annotation:
    db_annotation = models.Annotation(
        video_id=video_id,
        user_id=user_id,
        timestamp=annotation_data.timestamp,
        speed=annotation_data.speed,
        button_state=annotation_data.button_state,
    )
    db.add(db_annotation)
    await db.commit()
    await db.refresh(db_annotation)
    return db_annotation

async def create_annotations_bulk(
    db: AsyncSession,
    video_id: str,
    user_id: str,
    annotations: List[dict]
) -> List[models.Annotation]:
    db_annotations = []
    for annotation in annotations:
        db_annotation = models.Annotation(
            video_id=video_id,
            user_id=user_id,
            **annotation
        )
        db_annotations.append(db_annotation)
    
    db.add_all(db_annotations)
    await db.commit()
    return db_annotations

# Video data operations
async def get_speed_data(db: AsyncSession, video_id: str) -> List[models.SpeedData]:
    result = await db.execute(
        select(models.SpeedData)
        .filter(models.SpeedData.video_id == video_id)
        .order_by(models.SpeedData.timestamp)
    )
    return result.scalars().all()

async def get_button_data(db: AsyncSession, video_id: str) -> List[models.ButtonData]:
    result = await db.execute(
        select(models.ButtonData)
        .filter(models.ButtonData.video_id == video_id)
        .order_by(models.ButtonData.timestamp)
    )
    return result.scalars().all()

# Timestamp operations
async def update_video_timestamp_offset(
    db: AsyncSession,
    video_id: str,
    timestamp_offset: float
) -> models.Video:
    video = await get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
        
    video.timestamp_offset = timestamp_offset
    await db.commit()
    await db.refresh(video)
    return video

async def update_button_data_timestamp_offset(
    db: AsyncSession,
    video_id: str,
    timestamp_offset: float
) -> List[models.ButtonData]:
    result = await db.execute(
        select(models.ButtonData)
        .filter(models.ButtonData.video_id == video_id)
    )
    button_data = result.scalars().all()
    
    for data in button_data:
        data.timestamp_offset = timestamp_offset
    
    await db.commit()
    return button_data

async def add_video_timestamps(
    db: AsyncSession,
    video_id: str, 
    timestamps_data: List[dict]
) -> models.Video:
    """Add or update video timestamps"""
    video = await get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Update timestamps
    video.timestamps = timestamps_data
    await db.commit()
    await db.refresh(video)
    return video

# Lock operations
async def lock_video(
    db: AsyncSession,
    video_id: str,
    user_id: str
) -> models.Video:
    """Lock a video for annotation"""
    video = await get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
        
    if video.locked_by and video.locked_by != user_id:
        # Check if lock has expired
        if video.lock_time and (datetime.utcnow() - video.lock_time).total_seconds() < 3600:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Video is locked by another user"
            )
    
    video.locked_by = user_id
    video.lock_time = datetime.utcnow()
    video.status = "in_progress"
    
    await db.commit()
    await db.refresh(video)
    return video

async def unlock_video(
    db: AsyncSession,
    video_id: str,
    user_id: str
) -> models.Video:
    """Unlock a video after annotation"""
    video = await get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
        
    if video.locked_by != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to unlock this video"
        )
    
    video.locked_by = None
    video.lock_time = None
    video.status = "completed"
    
    await db.commit()
    await db.refresh(video)
    return video

# Inference operations
async def create_inference_results_bulk(
    db: AsyncSession,
    video_id: str,
    predictions: List[dict]
) -> List[models.InferenceResult]:
    db_results = []
    for pred in predictions:
        db_result = models.InferenceResult(
            video_id=video_id,
            timestamp=pred["timestamp"],
            predicted_speed=pred["predicted_speed"],
            confidence=pred.get("confidence", 1.0)
        )
        db_results.append(db_result)
    
    db.add_all(db_results)
    await db.commit()
    return db_results

async def get_inference_results(
    db: AsyncSession,
    video_id: str
) -> List[models.InferenceResult]:
    result = await db.execute(
        select(models.InferenceResult)
        .filter(models.InferenceResult.video_id == video_id)
        .order_by(models.InferenceResult.timestamp)
    )
    return result.scalars().all()