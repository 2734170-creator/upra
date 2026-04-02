from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.models import Account, Currency
from app.schemas import AccountCreate, AccountOut

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


async def _get_rub_id(db: AsyncSession) -> int:
    result = await db.execute(select(Currency).where(Currency.code == "RUB"))
    rub = result.scalar_one_or_none()
    return rub.id if rub else 1


async def _account_out(account, db):
    curr = None
    if account.currency_id:
        curr = await db.get(Currency, account.currency_id)
    return AccountOut(
        id=account.id,
        name=account.name,
        type=account.type,
        company_id=account.company_id,
        currency_id=account.currency_id,
        currency_code=curr.code if curr else "",
    )


@router.get("", response_model=list[AccountOut])
async def list_accounts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Account).order_by(Account.name))
    accounts = result.scalars().all()
    return [await _account_out(a, db) for a in accounts]


@router.post("", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
async def create_account(data: AccountCreate, db: AsyncSession = Depends(get_db)):
    currency_id = data.currency_id
    if not currency_id:
        currency_id = await _get_rub_id(db)
    account = Account(
        name=data.name,
        company_id=data.company_id,
        type=data.type,
        currency_id=currency_id,
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return await _account_out(account, db)


@router.get("/{account_id}", response_model=AccountOut)
async def get_account(account_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return await _account_out(account, db)


@router.put("/{account_id}", response_model=AccountOut)
async def update_account(
    account_id: int, data: AccountCreate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    for key, value in data.model_dump().items():
        setattr(account, key, value)
    await db.commit()
    await db.refresh(account)
    return await _account_out(account, db)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    await db.delete(account)
    await db.commit()
