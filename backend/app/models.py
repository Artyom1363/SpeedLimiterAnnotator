# Path: backend/app/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
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

    # Отношения с явным указанием внешних ключей
    videos = relationship(
        "Video",
        foreign_keys="[Video.user_id]",
        back_populates="user"
    )
    locked_videos = relationship(
        "Video",
        foreign_keys="[Video.locked_by]",
        back_populates="locked_by_user"
    )
    annotations = relationship("Annotation", back_populates="user")

class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String)
    s3_key = Column(String)
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="unannotated")  # unannotated, in_progress, completed
    
    # Внешние ключи с явными именами отношений
    user_id = Column(String, ForeignKey("users.id"))
    locked_by = Column(String, ForeignKey("users.id"), nullable=True)
    lock_time = Column(DateTime, nullable=True)

    # Отношения
    user = relationship(
        "User", 
        foreign_keys=[user_id],
        back_populates="videos"
    )
    locked_by_user = relationship(
        "User",
        foreign_keys=[locked_by],
        back_populates="locked_videos"
    )
    speed_data = relationship("SpeedData", back_populates="video")
    button_data = relationship("ButtonData", back_populates="video")
    annotations = relationship("Annotation", back_populates="video")

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

    # Отношения
    video = relationship("Video", back_populates="speed_data")

class ButtonData(Base):
    __tablename__ = "button_data"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String, ForeignKey("videos.id"))
    timestamp = Column(Float)
    state = Column(Boolean)

    # Отношения
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
    created_at = Column(DateTime, default=datetime.utcnow)

    # Отношения
    video = relationship("Video", back_populates="annotations")
    user = relationship("User", back_populates="annotations")