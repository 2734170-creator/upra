from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.models import BudgetItem
from app.schemas import BudgetItemCreate, BudgetItemOut

router = APIRouter(prefix="/api/budget-items", tags=["budget-items"])


@router.get("", response_model=list[BudgetItemOut])
async def list_budget_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BudgetItem))
    return result.scalars().all()


@router.post("", response_model=BudgetItemOut, status_code=status.HTTP_201_CREATED)
async def create_budget_item(
    data: BudgetItemCreate, db: AsyncSession = Depends(get_db)
):
    item = BudgetItem(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/{item_id}", response_model=BudgetItemOut)
async def get_budget_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BudgetItem).where(BudgetItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Budget item not found")
    return item


@router.put("/{item_id}", response_model=BudgetItemOut)
async def update_budget_item(
    item_id: int, data: BudgetItemCreate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(BudgetItem).where(BudgetItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Budget item not found")
    for key, value in data.model_dump().items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BudgetItem).where(BudgetItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Budget item not found")
    await db.delete(item)
    await db.commit()
