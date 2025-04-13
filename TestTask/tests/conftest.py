import os

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.session import Base

from sqlalchemy.sql import text

from app.main import app

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
test_async_session = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Creates a session for interacting with the test database."""
    async with test_async_session() as session:
        yield session

    # Clean up the database after tests
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f"TRUNCATE {table.name} RESTART IDENTITY CASCADE"))
        await conn.commit()

@pytest_asyncio.fixture
async def async_client():
    """Создает асинхронный клиент для тестирования FastAPI приложения."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client



@pytest_asyncio.fixture(autouse=True)
async def clean_db(db_session):
    """Cleans the database before each test."""
    for table in reversed(Base.metadata.sorted_tables):
        await db_session.execute(text(f"TRUNCATE {table.name} RESTART IDENTITY CASCADE"))
    await db_session.commit()