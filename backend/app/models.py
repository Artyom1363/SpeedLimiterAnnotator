# Path: backend/app/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    videos = relationship("Video", foreign_keys="[Video.user_id]", back_populates="user")
    locked_videos = relationship("Video", foreign_keys="[Video.locked_by]", back_populates="locked_by_user")
    annotations = relationship("Annotation", back_populates="user")

    def get_token(self) -> str:
        """Generate JWT token for this user"""
        from app.dependencies import create_access_token
        from datetime import timedelta
        data = {"sub": str(self.id)}
        expires_delta = timedelta(minutes=30)
        return create_access_token(data=data, expires_delta=expires_delta)


class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String)
    s3_key = Column(String)
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="unannotated")  # unannotated, in_progress, completed
    timestamp_offset = Column(Float, default=0.0)  # For video time synchronization
    
    user_id = Column(String, ForeignKey("users.id"))
    locked_by = Column(String, ForeignKey("users.id"), nullable=True)
    lock_time = Column(DateTime, nullable=True)

    user = relationship("User", foreign_keys=[user_id], back_populates="videos")
    locked_by_user = relationship("User", foreign_keys=[locked_by], back_populates="locked_videos")
    speed_data = relationship("SpeedData", back_populates="video", cascade="all, delete-orphan")
    button_data = relationship("ButtonData", back_populates="video", cascade="all, delete-orphan")
    annotations = relationship("Annotation", back_populates="video", cascade="all, delete-orphan")
    inference_results = relationship("InferenceResult", back_populates="video", cascade="all, delete-orphan")

class SpeedData(Base):
    __tablename__ = "speed_data"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String, ForeignKey("videos.id"))
    timestamp = Column(Float)
    speed = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    accuracy = Column(Float)
    timestamp_offset = Column(Float, default=0.0)  # For speed data synchronization

    video = relationship("Video", back_populates="speed_data")

class ButtonData(Base):
    __tablename__ = "button_data"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String, ForeignKey("videos.id"))
    timestamp = Column(Float)
    state = Column(Boolean)
    timestamp_offset = Column(Float, default=0.0)  # For button data synchronization

    video = relationship("Video", back_populates="button_data")

class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String, ForeignKey("videos.id"))
    user_id = Column(String, ForeignKey("users.id"))
    timestamp = Column(Float)
    speed = Column(Float)
    button_state = Column(Boolean)
    error_detected = Column(Boolean, default=False)
    annotation_data = Column(JSON, default={})  # Переименовали metadata в annotation_data
    created_at = Column(DateTime, default=datetime.utcnow)

    video = relationship("Video", back_populates="annotations")
    user = relationship("User", back_populates="annotations")

class InferenceResult(Base):
    __tablename__ = "inference_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String, ForeignKey("videos.id"))
    timestamp = Column(Float)
    predicted_speed = Column(Float)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    video = relationship("Video", back_populates="inference_results")