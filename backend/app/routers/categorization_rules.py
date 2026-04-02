from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.models import CategorizationRule
from app.schemas import CategorizationRuleCreate, CategorizationRuleOut

router = APIRouter(prefix="/api/categorization-rules", tags=["categorization-rules"])


@router.get("", response_model=list[CategorizationRuleOut])
async def list_rules(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CategorizationRule))
    return result.scalars().all()


@router.post(
    "", response_model=CategorizationRuleOut, status_code=status.HTTP_201_CREATED
)
async def create_rule(
    data: CategorizationRuleCreate, db: AsyncSession = Depends(get_db)
):
    rule = CategorizationRule(**data.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.get("/{rule_id}", response_model=CategorizationRuleOut)
async def get_rule(rule_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CategorizationRule).where(CategorizationRule.id == rule_id)
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.put("/{rule_id}", response_model=CategorizationRuleOut)
async def update_rule(
    rule_id: int, data: CategorizationRuleCreate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(CategorizationRule).where(CategorizationRule.id == rule_id)
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    for key, value in data.model_dump().items():
        setattr(rule, key, value)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(rule_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CategorizationRule).where(CategorizationRule.id == rule_id)
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    await db.delete(rule)
    await db.commit()
