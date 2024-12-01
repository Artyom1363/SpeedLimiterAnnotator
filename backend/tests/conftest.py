# Path: backend/tests/conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from moto import mock_s3
import boto3
from typing import AsyncGenerator
import asyncio
from datetime import datetime
import uuid
from passlib.context import CryptContext

from app.database import Base, get_db
from app.main import app
from app.models import User

from .test_data import get_test_button_data_path, get_test_speed_data_path

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@test_db:5432/test_db"

# Настройки для тестового S3
TEST_BUCKET = "test-bucket"
TEST_REGION = "us-east-1"

# Password hasher для тестов
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
        isolation_level="AUTOCOMMIT"
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

@pytest.fixture
async def client(test_session) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with the test database session."""
    async def override_get_db():
        try:
            yield test_session
        finally:
            await test_session.close()

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        try:
            yield client
        finally:
            app.dependency_overrides.clear()

@pytest.fixture
def test_password() -> str:
    """Generate test password"""
    return "testpassword123"

@pytest.fixture
async def test_user(test_session, test_password) -> User:
    """Create a test user."""
    user = User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        username="testuser",
        hashed_password=pwd_context.hash(test_password),
        created_at=datetime.utcnow(),
        is_active=True
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user

@pytest.fixture
def s3():
    """Create a mocked S3 bucket."""
    with mock_s3():
        s3_client = boto3.client(
            's3',
            region_name=TEST_REGION,
            aws_access_key_id='testing',
            aws_secret_access_key='testing',
        )
        s3_client.create_bucket(Bucket=TEST_BUCKET)
        yield s3_client

@pytest.fixture
async def auth_headers(test_user) -> dict:
    """Generate authorization headers."""
    token = test_user.get_token()
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def video_file() -> tuple:
    """Create a test video file."""
    content = b"test video content"
    filename = "test.mp4"
    content_type = "video/mp4"
    return filename, content, content_type

@pytest.fixture
async def uploaded_video(
    client: AsyncClient,
    test_user: User,
    video_file: tuple,
    auth_headers: dict
) -> dict:
    """Helper fixture to create an uploaded video."""
    filename, content, content_type = video_file
    files = {"video_file": (filename, content, content_type)}
    
    response = await client.post(
        "/api/data/upload_video",
        files=files,
        headers=auth_headers
    )
    return response.json()

@pytest.fixture
async def video_with_data(
    client: AsyncClient,
    uploaded_video: dict,
    auth_headers: dict
) -> dict:
    """Helper fixture to create a video with speed and button data."""
    video_id = uploaded_video["video_id"]
    
    # Upload speed data
    with open(get_test_speed_data_path(), 'rb') as speed_file:
        await client.post(
            f"/api/data/upload_csv",
            files={"csv_file": ("speed_data.csv", speed_file, "text/csv")},
            params={"video_id": video_id},
            headers=auth_headers
        )
    
    # Upload button data
    with open(get_test_button_data_path(), 'rb') as button_file:
        await client.post(
            f"/api/data/upload_button_data",
            files={"button_data_file": ("button_data.txt", button_file, "text/plain")},
            params={"video_id": video_id},
            headers=auth_headers
        )
    
    return uploaded_video