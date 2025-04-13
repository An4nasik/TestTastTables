import asyncio
import logging
from fastapi import FastAPI
from app.db.session import engine, Base
import logging
from contextlib import asynccontextmanager
from app.routers import tables, reservations

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        for _ in range(5):  # Попытки подключения
            try:
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                logger.info("Database initialized successfully.")
                break
            except Exception as e:
                logger.error(f"Database not ready, retrying...: {e}")
                await asyncio.sleep(5)  # Задержка перед повторной попыткой
        else:
            raise Exception("Database connection failed after multiple attempts.")
        yield
    except Exception as e:
        logger.error(f"Error initializing the database: {e}")
        raise

app = FastAPI(lifespan=lifespan)
logger = logging.getLogger(__name__)

app.include_router(tables.router, prefix="/tables")
app.include_router(reservations.router, prefix="/reservations")


