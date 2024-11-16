# app/models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True, nullable=False)
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    file_metadata = Column(String, nullable=True)  # Renamed from 'metadata' to 'file_metadata'

