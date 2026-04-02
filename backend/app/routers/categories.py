from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.models import Category, MovementType, DdsSection
from app.schemas import CategoryCreate, CategoryOut, CategoryTreeNode

router = APIRouter(prefix="/api/categories", tags=["categories"])


async def _category_out(cat, db):
    pnl_name = None
    if cat.pnl_article_id:
        pnl = await db.get(Category, cat.pnl_article_id)
        if pnl:
            pnl_name = pnl.name
    return CategoryOut(
        id=cat.id,
        name=cat.name,
        type=cat.type,
        parent_id=cat.parent_id,
        is_pnl=cat.is_pnl,
        code=cat.code,
        movement_type=cat.movement_type,
        dds_section=cat.dds_section,
        pnl_article_id=cat.pnl_article_id,
        pnl_article_name=pnl_name,
        pnl_impact=cat.pnl_impact,
        is_active=cat.is_active,
        comment=cat.comment,
    )


@router.get("", response_model=list[CategoryOut])
async def list_categories(
    dds_section: str | None = Query(None),
    movement_type: str | None = Query(None),
    is_active: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    q = select(Category)
    if dds_section:
        q = q.where(Category.dds_section == DdsSection(dds_section))
    if movement_type:
        q = q.where(Category.movement_type == MovementType(movement_type))
    if is_active is not None:
        q = q.where(Category.is_active == is_active)
    result = await db.execute(q)
    cats = result.scalars().all()
    return [await _category_out(c, db) for c in cats]


@router.get("/tree", response_model=list[CategoryTreeNode])
async def get_category_tree(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.parent_id == None))
    roots = result.scalars().all()
    tree = []
    for root in roots:
        tree.append(await _build_tree(root, db))
    return tree


async def _build_tree(parent: Category, db: AsyncSession) -> CategoryTreeNode:
    result = await db.execute(select(Category).where(Category.parent_id == parent.id))
    children = result.scalars().all()
    return CategoryTreeNode(
        id=parent.id,
        name=parent.name,
        code=parent.code,
        movement_type=parent.movement_type,
        dds_section=parent.dds_section,
        children=[await _build_tree(c, db) for c in children],
    )


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    category = Category(**data.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return await _category_out(category, db)


@router.get("/{category_id}", response_model=CategoryOut)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return await _category_out(category, db)


@router.put("/{category_id}", response_model=CategoryOut)
async def update_category(
    category_id: int, data: CategoryCreate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in data.model_dump().items():
        setattr(category, key, value)
    await db.commit()
    await db.refresh(category)
    return await _category_out(category, db)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(category)
    await db.commit()
