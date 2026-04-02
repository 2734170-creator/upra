from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.models import Currency
from app.schemas import CurrencyCreate, CurrencyOut

router = APIRouter(prefix="/api/currencies", tags=["currencies"])

OKV_CURRENCIES = [
    {
        "code": "RUB",
        "numeric_code": "643",
        "name_ru": "Российский рубль",
        "symbol": "₽",
    },
    {"code": "USD", "numeric_code": "840", "name_ru": "Доллар США", "symbol": "$"},
    {"code": "EUR", "numeric_code": "978", "name_ru": "Евро", "symbol": "€"},
    {"code": "CNY", "numeric_code": "156", "name_ru": "Юань", "symbol": "¥"},
    {"code": "GBP", "numeric_code": "826", "name_ru": "Фунт стерлингов", "symbol": "£"},
    {"code": "JPY", "numeric_code": "392", "name_ru": "Иена", "symbol": "¥"},
    {
        "code": "CHF",
        "numeric_code": "756",
        "name_ru": "Швейцарский франк",
        "symbol": "CHF",
    },
    {"code": "TRY", "numeric_code": "949", "name_ru": "Турецкая лира", "symbol": "₺"},
    {"code": "KZT", "numeric_code": "398", "name_ru": "Тенге", "symbol": "₸"},
    {"code": "BTC", "numeric_code": "", "name_ru": "Биткоин", "symbol": "₿"},
    {"code": "ETH", "numeric_code": "", "name_ru": "Эфириум", "symbol": "Ξ"},
    {"code": "USDT", "numeric_code": "", "name_ru": "Тезер", "symbol": "₮"},
]


@router.post("/seed")
async def seed_currencies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Currency))
    existing = {c.code for c in result.scalars().all()}
    added = 0
    for c in OKV_CURRENCIES:
        if c["code"] not in existing:
            db.add(Currency(**c))
            added += 1
    await db.commit()
    return {"added": added, "total": len(OKV_CURRENCIES)}


@router.get("", response_model=list[CurrencyOut])
async def list_currencies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Currency).order_by(Currency.name_ru))
    return result.scalars().all()


@router.post("", response_model=CurrencyOut, status_code=status.HTTP_201_CREATED)
async def create_currency(data: CurrencyCreate, db: AsyncSession = Depends(get_db)):
    code = data.code or data.name_ru[:3].upper().strip()
    result = await db.execute(select(Currency).where(Currency.code == code))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Currency code already exists")
    currency = Currency(
        code=code,
        numeric_code=data.numeric_code,
        name_ru=data.name_ru,
        symbol=data.symbol,
    )
    db.add(currency)
    await db.commit()
    await db.refresh(currency)
    return currency


@router.put("/{currency_id}", response_model=CurrencyOut)
async def update_currency(
    currency_id: int, data: CurrencyCreate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Currency).where(Currency.id == currency_id))
    currency = result.scalar_one_or_none()
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    for key, value in data.model_dump().items():
        setattr(currency, key, value)
    await db.commit()
    await db.refresh(currency)
    return currency


@router.delete("/{currency_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_currency(currency_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Currency).where(Currency.id == currency_id))
    currency = result.scalar_one_or_none()
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    await db.delete(currency)
    await db.commit()
