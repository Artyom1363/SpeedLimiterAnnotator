# Path: backend/app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.pool import NullPool
import os

# URL для асинхронного подключения
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://test:test@test_db:5432/test_db")

# Создаем асинхронный движок
async_engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=True
)

# Создаем фабрику сессий
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Создаем базовый класс для моделей
Base = declarative_base()

# Зависимость для получения сессии БД
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()