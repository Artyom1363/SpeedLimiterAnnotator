# Path: app/routers/videos.py
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

# Create uploads directory
UPLOAD_DIR = "/code/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(
    prefix="/api/data",
    tags=["videos"]
)

MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB

def get_s3_client():
    """Get configured S3 client"""
    return boto3.client(
        's3',
        endpoint_url=os.getenv('S3_ENDPOINT_URL', 'https://storage.yandexcloud.net'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name="ru-central1"
    ), os.getenv('S3_BUCKET_NAME', os.getenv('S3_BUCKET_NAME'))

@router.post("/upload_video", response_model=schemas.VideoUploadResponse, status_code=201)
async def upload_video(
    video_file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    s3_info: tuple = Depends(get_s3_client)
):
    try:
        # Логируем входные данные
        print(f"Starting upload for file: {video_file.filename}")
        print(f"Content type: {video_file.content_type}")
        print(f"User ID: {current_user.id}")
        
        if not video_file.content_type.startswith('video/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type"
            )

        s3_key = f"videos/{current_user.id}/{video_file.filename}"
        print(f"Generated S3 key: {s3_key}")
        
        try:
            # Создаем запись в БД
            video = await crud.create_video(
                db,
                filename=video_file.filename,
                s3_key=s3_key,
                user_id=current_user.id
            )
            print(f"Created DB record with ID: {video.id}")

            # Пытаемся загрузить в S3
            s3_client, bucket_name = s3_info
            print(f"Got S3 client and bucket: {bucket_name}")

            temp_file_path = f"{UPLOAD_DIR}/{video_file.filename}"
            print(f"Temp file path: {temp_file_path}")

            async with aiofiles.open(temp_file_path, 'wb') as out_file:
                content = await video_file.read()
                await out_file.write(content)
            print("File saved temporarily")

            with open(temp_file_path, 'rb') as file_data:
                print("Starting S3 upload...")
                s3_client.upload_fileobj(
                    file_data,
                    bucket_name,
                    s3_key,
                    ExtraArgs={'ContentType': video_file.content_type}
                )
                print("S3 upload complete")

        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                print("Temp file removed")

        return {
            "status": "success",
            "message": "Video uploaded successfully",
            "video_id": video.id
        }

    except Exception as e:
        print(f"Error during video upload: {str(e)}")
        print(f"Error type: {type(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/upload_csv/{video_id}", response_model=schemas.StandardResponse)
async def upload_csv(
    video_id: str,
    csv_file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    video = await crud.get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    if video.user_id != current_user.id and video.locked_by != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")

    try:
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
        
        await crud.create_speed_data_bulk(db, video_id, speed_data)
        
        return {
            "status": "success",
            "message": "CSV data uploaded successfully"
        }
    except (ValueError, KeyError) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid CSV format: {str(e)}"
        )

@router.post("/upload_button_data/{video_id}", response_model=schemas.StandardResponse) 
async def upload_button_data(
    video_id: str,
    button_data_file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    video = await crud.get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if video.user_id != current_user.id and video.locked_by != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")

    try:
        content = await button_data_file.read()
        lines = content.decode().splitlines()
        button_data = []
        
        for line in lines:
            timestamp, state = line.strip().split(',')
            button_data.append({
                'timestamp': float(timestamp),
                'state': state == '1'
            })
        
        await crud.create_button_data_bulk(db, video_id, button_data)
        
        return {
            "status": "success",
            "message": "Button data uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/next_unannotated", response_model=schemas.DataResponse)
async def get_next_unannotated(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    video = await crud.get_next_unannotated_video(db)
    if not video:
        raise HTTPException(status_code=404, detail="No unannotated videos available")

    return {
        "status": "success",
        "message": "Next video retrieved",
        "data": {
            "video_id": video.id,
            "filename": video.filename,
            "upload_date": video.upload_date,
            "status": video.status
        }
    }

@router.get("/video/{video_id}/data", response_model=schemas.DataResponse)
async def get_video_data(
    video_id: str,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    video = await crud.get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    speed_data = await crud.get_speed_data(db, video_id)
    button_data = await crud.get_button_data(db, video_id)
    
    return {
        "status": "success",
        "message": "Video data retrieved",
        "data": {
            "video_id": video.id,
            "speed_data": [
                {
                    "timestamp": data.timestamp,
                    "speed": data.speed,
                    "latitude": data.latitude,
                    "longitude": data.longitude
                } for data in speed_data
            ],
            "button_data": [
                {
                    "timestamp": data.timestamp,
                    "state": data.state
                } for data in button_data
            ]
        }
    }