# Path: backend/app/routers/videos.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List
from .. import crud, schemas, models
from ..database import get_db
from ..dependencies import get_current_user, get_video_or_404, check_video_lock
from starlette.background import BackgroundTask
import csv
import io
import aiofiles
import os
import boto3
from botocore.exceptions import ClientError
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse

# Create uploads directory
UPLOAD_DIR = "/code/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(
    prefix="/api/data",
    tags=["videos"]
)

MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB

async def get_s3_client():
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
    if not video_file.content_type.startswith('video/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type"
        )

    temp_file_path = None
    try:
        s3_key = f"videos/{current_user.id}/{video_file.filename}"
        video = await crud.create_video(
            db,
            filename=video_file.filename,
            s3_key=s3_key,
            user_id=current_user.id
        )

        s3_client, bucket_name = s3_info
        temp_file_path = f"{UPLOAD_DIR}/{video_file.filename}"

        async with aiofiles.open(temp_file_path, 'wb') as out_file:
            content = await video_file.read()
            await out_file.write(content)

        with open(temp_file_path, 'rb') as file_data:
            s3_client.upload_fileobj(
                file_data,
                bucket_name,
                s3_key,
                ExtraArgs={'ContentType': video_file.content_type}
            )

        return {
            "status": "success",
            "video_id": video.id,
            "message": "Video uploaded successfully"
        }

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@router.post("/upload_csv/{video_id}", response_model=schemas.StandardResponse)
async def upload_csv_data(
    video_id: str,
    csv_file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process speed data CSV"""
    video = await get_video_or_404(video_id, db)
    
    content = await csv_file.read()
    try:
        decoded_content = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded_content), skipinitialspace=True)
        
        required_columns = {
            'Elapsed time (sec)',
            'Speed (km/h)',
            'Latitude',
            'Longitude',
            'Altitude (km)',
            'Accuracy (km)'
        }
        
        first_row = next(csv_reader, None)
        if not first_row or not required_columns.issubset(set(first_row.keys())):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid CSV format. Required columns: {required_columns}"
            )

        rows = [first_row] + list(csv_reader)
        await crud.create_speed_data_bulk(db, video_id, rows)
        
        return {
            "status": "success",
            "message": "CSV data uploaded successfully"
        }
        
    except (UnicodeDecodeError, csv.Error) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid CSV format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
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

    content = await button_data_file.read()
    button_data = []
    try:
        lines = content.decode().splitlines()
        for line in lines:
            timestamp, state = line.strip().split(',')
            button_data.append({
                'timestamp': float(timestamp),
                'state': state == '1'
            })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid button data format: {str(e)}"
        )

    await crud.create_button_data_bulk(db, video_id, button_data)
    
    return {
        "status": "success",
        "message": "Button data uploaded successfully"
    }

@router.post("/add_video_timestamp/{video_id}", response_model=schemas.StandardResponse)
async def add_video_timestamp(
    video_id: str,
    video_data_with_timestamps: List[dict], 
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    video = await get_video_or_404(video_id, db)
    await crud.add_video_timestamps(db, video_id, video_data_with_timestamps)
    
    return {
        "status": "success",
        "message": "Video timestamps added/adjusted successfully"
    }

@router.get("/{video_id}/data", response_model=schemas.DataResponse)
async def get_video_data(
    video_id: str,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    video = await get_video_or_404(video_id, db)
    speed_data = await crud.get_speed_data(db, video_id)
    button_data = await crud.get_button_data(db, video_id)
    
    return {
        "status": "success",
        "message": "Video data retrieved successfully",
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

@router.api_route("/video/{video_id}", methods=["GET", "HEAD"])
async def get_video_file(
    video_id: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    video = await crud.get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    try:
        s3_client, bucket_name = await get_s3_client()
        
        # Получаем объект напрямую из S3
        try:
            s3_response = s3_client.get_object(
                Bucket=bucket_name,
                Key=video.s3_key
            )
            
            # Настраиваем заголовки для стриминга
            response.headers["Content-Type"] = "video/mp4"
            response.headers["Accept-Ranges"] = "bytes"
            response.headers["Content-Length"] = str(s3_response['ContentLength'])
            
            # Возвращаем тело ответа как стрим
            return StreamingResponse(
                s3_response['Body'].iter_chunks(),
                media_type="video/mp4",
                headers={
                    "Content-Disposition": f'inline; filename="{video.filename}"',
                    "Accept-Ranges": "bytes"
                }
            )
            
        except Exception as e:
            print(f"S3 error: {str(e)}")
            raise HTTPException(status_code=404, detail="Video not found in S3")
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_file_size(s3_client, bucket_name: str, key: str) -> int:
    try:
        response = s3_client.head_object(Bucket=bucket_name, Key=key)
        return response['ContentLength']
    except Exception:
        return 0