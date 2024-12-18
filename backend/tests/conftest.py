# Path: backend/tests/conftest.py
import os
import pytest
from httpx import AsyncClient
from app.routers.videos import get_s3_client
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
import boto3
from typing import AsyncGenerator
import asyncio
from datetime import datetime
import uuid
from passlib.context import CryptContext
import aiofiles  # Добавлен импорт

from app.database import Base, get_db
from app.main import app
from app.models import User
from .test_data import get_test_button_data_path, get_test_speed_data_path

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@test_db:5432/test_db"

# Password hasher for tests
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        isolation_level="AUTOCOMMIT"
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture(scope="function")
async def test_s3_client():
    return boto3.client(
        's3',
        endpoint_url=os.getenv('S3_ENDPOINT_URL'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name="ru-central1"
    ), os.getenv('S3_TEST_BUCKET')

@pytest.fixture(scope="function")
async def client(test_session, test_s3_client) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""
    async def override_get_db():
        yield test_session
        
    async def override_get_s3_client():
        return test_s3_client

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_s3_client] = override_get_s3_client
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session

@pytest.fixture
def test_password() -> str:
    """Generate test password"""
    return "testpassword123"

@pytest.fixture(scope="function")
async def test_user(test_session) -> User:
    user = User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        username="testuser",
        hashed_password=pwd_context.hash("password123"),
        created_at=datetime.utcnow(),
        is_active=True
    )
    test_session.add(user)
    await test_session.commit()
    return user

@pytest.fixture(scope="function")
async def test_user2(test_session) -> User:
    user = User(
        id=str(uuid.uuid4()),
        email="test2@example.com", 
        username="testuser2",
        hashed_password=pwd_context.hash("password123"),
        created_at=datetime.utcnow(),
        is_active=True
    )
    test_session.add(user)
    await test_session.commit()
    return user

@pytest.fixture(scope="function")
def s3():
    s3_client = boto3.client(
        's3',
        endpoint_url=os.getenv('S3_ENDPOINT_URL'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), 
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name="ru-central1"
    )
    print(f"debug s3: {os.getenv('S3_ENDPOINT_URL')=}, {os.getenv('AWS_ACCESS_KEY_ID')=}, {os.getenv('AWS_SECRET_ACCESS_KEY')=}, {os.getenv('S3_TEST_BUCKET')=}")
    return s3_client, os.getenv('S3_TEST_BUCKET')


@pytest.fixture(scope="function")
async def auth_headers(test_user) -> dict:
    """Generate authorization headers."""
    token = test_user.get_token()
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def video_file() -> tuple:
    """Create a test video file."""
    content = b"test video content"
    filename = "test_video.mp4"
    content_type = "video/mp4"
    return filename, content, content_type

@pytest.fixture(scope="function")
async def uploaded_video(client: AsyncClient, test_user: User, video_file: tuple, auth_headers: dict) -> dict:
    """Helper fixture to create an uploaded video."""
    filename, content, content_type = video_file
    files = {"video_file": (filename, content, content_type)}
    
    response = await client.post(
        "/api/data/upload_video",
        files=files,
        headers=auth_headers
    )
    return response.json()

@pytest.fixture(scope="function")
async def video_with_data(client: AsyncClient, uploaded_video: dict, auth_headers: dict) -> dict:
    """Helper fixture to create a video with speed and button data."""
    video_id = uploaded_video["data"]["video_id"]
    
    async with aiofiles.open(get_test_speed_data_path(), 'rb') as speed_file:
        await client.post(
            f"/api/data/upload_csv",
            files={"csv_file": ("speed_data.csv", await speed_file.read(), "text/csv")},
            params={"video_id": video_id},
            headers=auth_headers
        )
    
    async with aiofiles.open(get_test_button_data_path(), 'rb') as button_file:
        await client.post(
            f"/api/data/upload_button_data",
            files={"button_data_file": ("button_data.txt", await button_file.read(), "text/plain")},
            params={"video_id": video_id},
            headers=auth_headers
        )
    
    return uploaded_video
