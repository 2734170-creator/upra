from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.models import Counterparty
from app.schemas import CounterpartyCreate, CounterpartyOut

router = APIRouter(prefix="/api/counterparties", tags=["counterparties"])


@router.get("", response_model=list[CounterpartyOut])
async def list_counterparties(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Counterparty))
    return result.scalars().all()


@router.post("", response_model=CounterpartyOut, status_code=status.HTTP_201_CREATED)
async def create_counterparty(
    data: CounterpartyCreate, db: AsyncSession = Depends(get_db)
):
    item = Counterparty(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/{counterparty_id}", response_model=CounterpartyOut)
async def get_counterparty(counterparty_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Counterparty).where(Counterparty.id == counterparty_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Counterparty not found")
    return item


@router.put("/{counterparty_id}", response_model=CounterpartyOut)
async def update_counterparty(
    counterparty_id: int, data: CounterpartyCreate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Counterparty).where(Counterparty.id == counterparty_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Counterparty not found")
    for key, value in data.model_dump().items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{counterparty_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_counterparty(counterparty_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Counterparty).where(Counterparty.id == counterparty_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Counterparty not found")
    await db.delete(item)
    await db.commit()
