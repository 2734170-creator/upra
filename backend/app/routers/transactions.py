from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
from app.dependencies import get_db
from app.models import Transaction
from app.schemas import TransactionCreate, TransactionUpdate, TransactionOut

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionOut])
async def list_transactions(
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    account_id: int | None = Query(None),
    category_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    q = select(Transaction)
    if date_from:
        q = q.where(Transaction.date >= date_from)
    if date_to:
        q = q.where(Transaction.date <= date_to)
    if account_id:
        q = q.where(Transaction.account_id == account_id)
    if category_id:
        q = q.where(Transaction.category_id == category_id)
    q = q.order_by(Transaction.date.desc())
    result = await db.execute(q)
    return result.scalars().all()


@router.post("", response_model=TransactionOut, status_code=201)
async def create_transaction(
    data: TransactionCreate, db: AsyncSession = Depends(get_db)
):
    tx = Transaction(**data.model_dump())
    db.add(tx)
    await db.commit()
    await db.refresh(tx)
    return tx


@router.get("/{tx_id}", response_model=TransactionOut)
async def get_transaction(tx_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Transaction).where(Transaction.id == tx_id))
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.put("/{tx_id}", response_model=TransactionOut)
async def update_transaction(
    tx_id: int, data: TransactionUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Transaction).where(Transaction.id == tx_id))
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tx, key, value)
    await db.commit()
    await db.refresh(tx)
    return tx


@router.delete("/{tx_id}", status_code=204)
async def delete_transaction(tx_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Transaction).where(Transaction.id == tx_id))
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    await db.delete(tx)
    await db.commit()
