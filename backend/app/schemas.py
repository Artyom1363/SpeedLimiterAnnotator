# Path: backend/app/schemas.py
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Union

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    pass

class UserInDB(UserBase):
    id: str
    created_at: datetime
    is_active: bool
    role: str

    model_config = ConfigDict(from_attributes=True)

class User(UserInDB):
    pass

# Auth schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None

class LoginData(BaseModel):
    email: EmailStr
    password: str

class VideoUploadResponse(BaseModel):
    status: str
    message: str 
    video_id: str

class UserRegisterResponse(BaseModel):
    status: str
    message: str
    user_id: str

# Video schemas
class VideoBase(BaseModel):
    filename: str

class VideoCreate(VideoBase):
    pass

class Video(VideoBase):
    id: str
    s3_key: str
    upload_date: datetime
    status: str
    user_id: str
    locked_by: Optional[str]
    lock_time: Optional[datetime]
    timestamp_offset: float

    model_config = ConfigDict(from_attributes=True)

# Speed data schemas
class SpeedDataCreate(BaseModel):
    timestamp: float
    speed: float
    latitude: float
    longitude: float
    altitude: float
    accuracy: float

class SpeedData(SpeedDataCreate):
    id: str
    video_id: str
    timestamp_offset: float

    model_config = ConfigDict(from_attributes=True)

# Button data schemas
class ButtonDataCreate(BaseModel):
    timestamp: float
    state: bool

class ButtonData(ButtonDataCreate):
    id: str
    video_id: str
    timestamp_offset: float

    model_config = ConfigDict(from_attributes=True)

# Annotation schemas
class AnnotationCreate(BaseModel):
    timestamp: float
    speed: float
    button_state: bool
    error_detected: bool = False
    metadata: Dict = {}

class Annotation(AnnotationCreate):
    id: str
    video_id: str
    user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Inference schemas
class InferenceResult(BaseModel):
    timestamp: float
    predicted_speed: float
    confidence: float

    model_config = ConfigDict(from_attributes=True)

# Response schemas
class StandardResponse(BaseModel):
    status: str
    message: str

class DataResponse(StandardResponse):
    data: Dict

class ErrorResponse(StandardResponse):
    error_code: Optional[str] = None
    details: Optional[Dict] = None