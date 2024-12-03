# Path: backend/app/schemas.py
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Union, Any

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: str
    created_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class User(UserInDB):
    pass

class UserRegisterResponse(BaseModel):
    status: str
    message: str
    user_id: str

# Auth schemas
class Token(BaseModel):
    status: str = "success"
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None

class LoginData(BaseModel):
    email: EmailStr
    password: str

# Response schemas
class StandardResponse(BaseModel):
    status: str
    message: str

class DataResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]

class VideoUploadResponse(StandardResponse):
    video_id: str

# Video schemas
class VideoBase(BaseModel):
    title: str

class VideoCreate(VideoBase):
    pass

class Video(VideoBase):
    video_id: str
    upload_date: datetime
    status: str
    locked_by: Optional[str]
    lock_time: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

# Annotation schemas
class AnnotationCreate(BaseModel):
    timestamp: float
    speed: float
    button_state: bool

class Annotation(AnnotationCreate):
    video_id: str
    user_id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AnnotationResponse(BaseModel):
    status: str
    video_id: str
    annotations: List[AnnotationCreate]

# Next unannotated video response
class NextVideoResponse(BaseModel):
    video_id: str
    title: str 
    upload_date: datetime
    status: str
    locked_by: Optional[str]
    lock_time: Optional[datetime]

# Lock response
class LockResponse(BaseModel):
    status: str
    video_id: str
    user_id: str
    locked_by: str
    lock_time: datetime

class UnlockResponse(BaseModel):
    status: str
    video_id: str

class TimestampShiftResponse(StandardResponse):
    pass

# Inference schemas
class InferenceResult(BaseModel):
    timestamp: float
    predicted_speed: float
    confidence: float

class InferenceResponse(BaseModel):
    status: str
    video_id: str
    predictions: List[InferenceResult]

# Geolocation schemas
class LocationPoint(BaseModel):
    timestamp: float
    latitude: float
    longitude: float

class GeolocationResponse(BaseModel):
    video_id: str
    locations: List[LocationPoint]