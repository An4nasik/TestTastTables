from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.table import Table
from app.schemas.table import TableCreate, TableResponse

router = APIRouter()

@router.post("/", response_model=TableResponse)
async def create_table(
    table: TableCreate,
    db: AsyncSession = Depends(get_db)
):
    new_table = Table(**table.model_dump())
    db.add(new_table)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(400, "Table creation failed")
    return new_table

@router.get("/", response_model=list[TableResponse])
async def get_tables(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Table))
    return result.scalars().all()