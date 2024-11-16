# app/schemas.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class VideoCreate(BaseModel):
    filename: str
    file_metadata: Optional[str] = None

class Video(BaseModel):
    id: int
    filename: str
    upload_time: datetime
    file_metadata: Optional[str]

    model_config = ConfigDict(from_attributes=True)

