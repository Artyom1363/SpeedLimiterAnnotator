# Path: backend/app/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from . import models, schemas
from typing import List, Optional

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
        user_id=user_id
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
    # Get videos that are either unannotated or have an expired lock
    result = await db.execute(
        select(models.Video)
        .filter(
            or_(
                models.Video.status == "unannotated",
                and_(
                    models.Video.status == "in_progress",
                    models.Video.lock_time < datetime.utcnow() - timedelta(hours=1)
                )
            )
        )
        .order_by(models.Video.upload_date)
    )
    return result.scalar_one_or_none()

# Speed data operations
async def create_speed_data_bulk(
    db: AsyncSession,
    video_id: str,
    speed_data: List[dict]
) -> List[models.SpeedData]:
    db_speed_data = [
        models.SpeedData(video_id=video_id, **data)
        for data in speed_data
    ]
    db.add_all(db_speed_data)
    await db.commit()
    return db_speed_data

# Button data operations
async def create_button_data_bulk(
    db: AsyncSession,
    video_id: str,
    button_data: List[dict]
) -> List[models.ButtonData]:
    db_button_data = [
        models.ButtonData(video_id=video_id, **data)
        for data in button_data
    ]
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
        **annotation_data.dict()
    )
    db.add(db_annotation)
    await db.commit()
    await db.refresh(db_annotation)
    return db_annotation

# Path: backend/app/crud.py
# Add these functions to the existing crud.py file

async def update_video_timestamp_offset(
    db: AsyncSession,
    video_id: str,
    timestamp_offset: float
) -> models.Video:
    video = await get_video(db, video_id)
    if video:
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

async def create_inference_results_bulk(
    db: AsyncSession,
    video_id: str,
    predictions: List[dict]
) -> List[models.InferenceResult]:
    db_results = [
        models.InferenceResult(
            video_id=video_id,
            timestamp=pred["timestamp"],
            predicted_speed=pred["predicted_speed"],
            confidence=pred["confidence"]
        )
        for pred in predictions
    ]
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

async def get_speed_data(
    db: AsyncSession,
    video_id: str
) -> List[models.SpeedData]:
    result = await db.execute(
        select(models.SpeedData)
        .filter(models.SpeedData.video_id == video_id)
        .order_by(models.SpeedData.timestamp)
    )
    return result.scalars().all()

async def get_button_data(
    db: AsyncSession,
    video_id: str
) -> List[models.ButtonData]:
    result = await db.execute(
        select(models.ButtonData)
        .filter(models.ButtonData.video_id == video_id)
        .order_by(models.ButtonData.timestamp)
    )
    return result.scalars().all()