from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.models import Company, Currency
from app.schemas import CompanyCreate, CompanyOut

router = APIRouter(prefix="/api/companies", tags=["companies"])


async def _get_rub_id(db: AsyncSession) -> int:
    result = await db.execute(select(Currency).where(Currency.code == "RUB"))
    rub = result.scalar_one_or_none()
    return rub.id if rub else 1


async def _company_out(company, db):
    curr = None
    if company.currency_id:
        curr = await db.get(Currency, company.currency_id)
    return CompanyOut(
        id=company.id,
        name=company.name,
        type=company.type,
        currency_id=company.currency_id,
        currency_code=curr.code if curr else "",
    )


@router.get("", response_model=list[CompanyOut])
async def list_companies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).order_by(Company.name))
    companies = result.scalars().all()
    return [await _company_out(c, db) for c in companies]


@router.post("", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
async def create_company(data: CompanyCreate, db: AsyncSession = Depends(get_db)):
    currency_id = data.currency_id
    if not currency_id:
        currency_id = await _get_rub_id(db)
    company = Company(name=data.name, type=data.type, currency_id=currency_id)
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return await _company_out(company, db)


@router.get("/{company_id}", response_model=CompanyOut)
async def get_company(company_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return await _company_out(company, db)


@router.put("/{company_id}", response_model=CompanyOut)
async def update_company(
    company_id: int, data: CompanyCreate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    for key, value in data.model_dump().items():
        setattr(company, key, value)
    await db.commit()
    await db.refresh(company)
    return await _company_out(company, db)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(company_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    await db.delete(company)
    await db.commit()
