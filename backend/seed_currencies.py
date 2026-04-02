import asyncio
from sqlalchemy import select
from app.database import async_session
from app.models import Currency

OKV = [
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


async def main():
    async with async_session() as db:
        result = await db.execute(select(Currency))
        existing = {c.code for c in result.scalars().all()}
        added = 0
        for c in OKV:
            if c["code"] not in existing:
                db.add(Currency(**c))
                existing.add(c["code"])
                added += 1
        await db.commit()
    print(f"Seeded {added} currencies")


asyncio.run(main())
