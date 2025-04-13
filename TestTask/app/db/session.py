from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()
from app.config import settings

engine = create_async_engine(str(settings.DATABASE_URL), echo=True, pool_size=10, max_overflow=20)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


import logging
logger = logging.getLogger(__name__)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()