from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.reservation import Reservation
from app.models.table import Table
from app.schemas.reservation import ReservationCreate, ReservationResponse
from app.services.reservation import ReservationService

router = APIRouter()


@router.post("/", response_model=ReservationResponse)
async def create_reservation(
        reservation: ReservationCreate,
        db: AsyncSession = Depends(get_db)
):
    # Проверка существования столика
    table = await db.get(Table, reservation.table_id)
    if not table:
        raise HTTPException(404, "Table not found")

    conflict = await ReservationService.check_time_conflict(
        reservation.table_id,
        reservation.reservation_time,
        reservation.duration_minutes
    )

    if conflict:
        raise HTTPException(409, "Time slot already booked")

    new_reservation = Reservation(**reservation.dict())
    db.add(new_reservation)
    try:
        await db.commit()
        await db.refresh(new_reservation)
    except Exception as e:
        await db.rollback()
        raise HTTPException(400, "Reservation creation failed")
    return new_reservation