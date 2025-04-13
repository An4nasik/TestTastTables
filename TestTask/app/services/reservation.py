from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError
from app.db.session import async_session
from app.models.reservation import Reservation


class ReservationService:
    @staticmethod
    async def check_time_conflict(
            table_id: int,
            start_time: datetime,
            duration: int
    ) -> bool:
        end_time = start_time + timedelta(minutes=duration)

        async with async_session() as session:
            result = await session.execute(
                select(Reservation).where(
                    and_(
                        Reservation.table_id == table_id,
                        Reservation.reservation_time < end_time,
                        Reservation.reservation_time + timedelta(minutes=Reservation.duration_minutes) > start_time
                    )
                )
            )
            return result.scalars().first() is not None