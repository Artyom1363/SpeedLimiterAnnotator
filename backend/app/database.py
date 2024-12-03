# Path: backend/app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import AsyncGenerator
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://artem:post_pass@db/speedlimiter-postgres")

async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()