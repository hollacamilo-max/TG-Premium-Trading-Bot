from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)
from sqlalchemy.orm import DeclarativeBase
from config import get_settings


class Base(DeclarativeBase):
    pass


engine: AsyncEngine | None = None
async_session_maker: async_sessionmaker[AsyncSession] | None = None


def init_db() -> None:
    global engine, async_session_maker
    settings = get_settings()
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.LOG_LEVEL == "DEBUG",
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )


async def close_db() -> None:
    global engine
    if engine:
        await engine.dispose()
        engine = None


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if async_session_maker is None:
        init_db()
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
