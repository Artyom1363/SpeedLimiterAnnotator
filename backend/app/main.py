# Path: backend/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import videos
from app.database import async_engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем таблицы при запуске
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup (если нужно)
    pass

app = FastAPI(lifespan=lifespan)

app.include_router(videos.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)