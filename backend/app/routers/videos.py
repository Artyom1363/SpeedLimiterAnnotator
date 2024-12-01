# Path: backend/app/routers/videos.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .. import crud, schemas, models
from ..database import get_db
from ..dependencies import get_current_user, get_video_or_404, check_video_lock
import csv
import io
import aiofiles
import os
import boto3
from botocore.exceptions import ClientError

router = APIRouter(
    prefix="/api/data",
    tags=["videos"]
)

# Configure S3 client
s3_client = boto3.client(
    's3',
    endpoint_url=os.getenv('S3_ENDPOINT_URL'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)
BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

@router.post("/upload_video", response_model=schemas.DataResponse)
async def upload_video(
    video_file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not video_file.content_type.startswith('video/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a video"
        )
    
    # Generate S3 key
    s3_key = f"videos/{current_user.id}/{video_file.filename}"
    
    try:
        # Upload to S3
        await s3_client.upload_fileobj(
            video_file.file,
            BUCKET_NAME,
            s3_key,
            ExtraArgs={'ContentType': video_file.content_type}
        )
        
        # Create video record in database
        video = await crud.create_video(
            db,
            filename=video_file.filename,
            s3_key=s3_key,
            user_id=current_user.id
        )
        
        return {
            "status": "success",
            "message": "Video uploaded successfully",
            "data": {"video_id": video.id}
        }
        
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/upload_csv", response_model=schemas.StandardResponse)
async def upload_csv(
    video_id: str = Form(...),
    csv_file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    video = await get_video_or_404(video_id, db)
    await check_video_lock(video, current_user)
    
    if not csv_file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV"
        )
    
    try:
        # Read and parse CSV
        content = await csv_file.read()
        csv_data = csv.DictReader(io.StringIO(content.decode()))
        speed_data = []
        
        for row in csv_data:
            speed_data.append({
                'timestamp': float(row['timestamp']),
                'speed': float(row['speed']),
                'latitude': float(row['latitude']),
                'longitude': float(row['longitude']),
                'altitude': float(row.get('altitude', 0)),
                'accuracy': float(row.get('accuracy', 0))
            })
        
        # Store speed data
        await crud.create_speed_data_bulk(db, video_id, speed_data)
        
        return {
            "status": "success",
            "message": "CSV data uploaded successfully"
        }
        
    except (ValueError, KeyError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid CSV format: {str(e)}"
        )

@router.post("/upload_button_data", response_model=schemas.StandardResponse)
async def upload_button_data(
    video_id: str = Form(...),
    button_data_file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    video = await get_video_or_404(video_id, db)
    await check_video_lock(video, current_user)
    
    try:
        content = await button_data_file.read()
        lines = content.decode().splitlines()
        button_data = []
        
        for i, line in enumerate(lines):
            state = line.strip()
            if state not in ['0', '1']:
                raise ValueError(f"Invalid button state at line {i+1}")
            
            button_data.append({
                'timestamp': float(i),  # Using line number as timestamp
                'state': state == '1'
            })
        
        # Store button data
        await crud.create_button_data_bulk(db, video_id, button_data)
        
        return {
            "status": "success",
            "message": "Button data uploaded successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/next_unannotated", response_model=schemas.Video)
async def get_next_unannotated(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    video = await crud.get_next_unannotated_video(db)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No unannotated videos available"
        )
    return video