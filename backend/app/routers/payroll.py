from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.models import PayrollAccrual
from app.schemas import PayrollAccrualCreate, PayrollAccrualOut

router = APIRouter(prefix="/api/payroll", tags=["payroll"])


@router.get("", response_model=list[PayrollAccrualOut])
async def list_payroll(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PayrollAccrual))
    return result.scalars().all()


@router.post("", response_model=PayrollAccrualOut, status_code=status.HTTP_201_CREATED)
async def create_payroll(
    data: PayrollAccrualCreate, db: AsyncSession = Depends(get_db)
):
    item = PayrollAccrual(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/{payroll_id}", response_model=PayrollAccrualOut)
async def update_payroll(
    payroll_id: int, data: PayrollAccrualCreate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(PayrollAccrual).where(PayrollAccrual.id == payroll_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Payroll accrual not found")
    for key, value in data.model_dump().items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{payroll_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payroll(payroll_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PayrollAccrual).where(PayrollAccrual.id == payroll_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Payroll accrual not found")
    await db.delete(item)
    await db.commit()
