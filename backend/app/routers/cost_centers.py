from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.models import CostCenter
from app.schemas import CostCenterCreate, CostCenterOut

router = APIRouter(prefix="/api/cost-centers", tags=["cost-centers"])


@router.get("", response_model=list[CostCenterOut])
async def list_cost_centers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CostCenter))
    return result.scalars().all()


@router.post("", response_model=CostCenterOut, status_code=status.HTTP_201_CREATED)
async def create_cost_center(
    data: CostCenterCreate, db: AsyncSession = Depends(get_db)
):
    item = CostCenter(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/{cost_center_id}", response_model=CostCenterOut)
async def get_cost_center(cost_center_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CostCenter).where(CostCenter.id == cost_center_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Cost center not found")
    return item


@router.put("/{cost_center_id}", response_model=CostCenterOut)
async def update_cost_center(
    cost_center_id: int, data: CostCenterCreate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(CostCenter).where(CostCenter.id == cost_center_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Cost center not found")
    for key, value in data.model_dump().items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{cost_center_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cost_center(cost_center_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CostCenter).where(CostCenter.id == cost_center_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Cost center not found")
    await db.delete(item)
    await db.commit()
