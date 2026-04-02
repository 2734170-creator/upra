import asyncio
from sqlalchemy import select
from app.database import async_session
from app.models import Category, MovementType, DdsSection, PnlImpact

CATEGORIES = [
    # 11. Аренда опалубки (parent)
    {
        "code": "11",
        "name": "Аренда опалубки",
        "movement_type": "inflow",
        "dds_section": "operating",
        "is_pnl": True,
        "is_active": True,
    },
    {
        "code": "11.01",
        "name": "Аренда опалубки",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "11",
        "pnl_article_name": "Выручка от аренды опалубки",
        "pnl_impact": "income",
        "is_active": True,
    },
    {
        "code": "11.02",
        "name": "Возврат неотработанного аванса за аренду опалубки",
        "movement_type": "outflow",
        "dds_section": "operating",
        "parent_code": "11",
        "pnl_article_name": "Корректировка выручки (возврат аванса)",
        "pnl_impact": "expense",
        "is_active": True,
    },
    {
        "code": "11.03",
        "name": "Восстановление комплекта опалубки",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "11",
        "pnl_article_name": "Выручка от восстановления опалубки",
        "pnl_impact": "income",
        "is_active": True,
    },
    # 12. Аренда лесов (parent)
    {
        "code": "12",
        "name": "Аренда лесов",
        "movement_type": "inflow",
        "dds_section": "operating",
        "is_pnl": True,
        "is_active": True,
    },
    {
        "code": "12.01",
        "name": "Аренда строительных лесов",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "12",
        "pnl_article_name": "Выручка от аренды лесов",
        "pnl_impact": "income",
        "is_active": True,
    },
    {
        "code": "12.02",
        "name": "Возврат неотработанного аванса за аренду лесов",
        "movement_type": "outflow",
        "dds_section": "operating",
        "parent_code": "12",
        "pnl_article_name": "Корректировка выручки (возврат аванса)",
        "pnl_impact": "expense",
        "is_active": True,
    },
    {
        "code": "12.03",
        "name": "Восстановление комплекта лесов",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "12",
        "pnl_article_name": "Выручка от восстановления лесов",
        "pnl_impact": "income",
        "is_active": True,
    },
    # 13. Транспортировка (parent)
    {
        "code": "13",
        "name": "Транспортировка",
        "movement_type": "inflow",
        "dds_section": "operating",
        "is_pnl": True,
        "is_active": True,
    },
    {
        "code": "13.01",
        "name": "Транспортировка а.м. Вольво",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "13",
        "pnl_article_name": "Выручка от транспортировки",
        "pnl_impact": "income",
        "is_active": True,
    },
    {
        "code": "13.02",
        "name": "Транспортировка а.м. Газ",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "13",
        "pnl_article_name": "Выручка от транспортировки",
        "pnl_impact": "income",
        "is_active": True,
    },
    {
        "code": "13.03",
        "name": "Прочая транспортировка",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "13",
        "pnl_article_name": "Выручка от транспортировки",
        "pnl_impact": "income",
        "is_active": True,
    },
    # 14. Услуги инструктора (parent)
    {
        "code": "14",
        "name": "Услуги инструктора",
        "movement_type": "inflow",
        "dds_section": "operating",
        "is_pnl": True,
        "is_active": True,
    },
    {
        "code": "14.01",
        "name": "Сверхурочная работа инструктора",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "14",
        "pnl_article_name": "Выручка от услуг инструктора",
        "pnl_impact": "income",
        "is_active": True,
    },
    {
        "code": "14.02",
        "name": "Компенсация жилья и проезда",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "14",
        "pnl_article_name": "Выручка от услуг инструктора",
        "pnl_impact": "income",
        "is_active": True,
    },
    {
        "code": "14.03",
        "name": "Компенсация командировочных",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "14",
        "pnl_article_name": "Выручка от услуг инструктора",
        "pnl_impact": "income",
        "is_active": True,
    },
    # 15. Прочие услуги (parent)
    {
        "code": "15",
        "name": "Прочие услуги",
        "movement_type": "inflow",
        "dds_section": "operating",
        "is_pnl": True,
        "is_active": True,
    },
    {
        "code": "15.01",
        "name": "Разработка проекта",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "15",
        "pnl_article_name": "Выручка от прочих услуг",
        "pnl_impact": "income",
        "is_active": True,
    },
    {
        "code": "15.02",
        "name": "Чистка опалубки",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "15",
        "pnl_article_name": "Выручка от прочих услуг",
        "pnl_impact": "income",
        "is_active": True,
    },
    # 16. Продажи (parent)
    {
        "code": "16",
        "name": "Продажи",
        "movement_type": "inflow",
        "dds_section": "operating",
        "is_pnl": True,
        "is_active": True,
    },
    {
        "code": "16.01",
        "name": "Продажа элементов опалубки",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "16",
        "pnl_article_name": "Выручка от продажи опалубки",
        "pnl_impact": "income",
        "is_active": True,
    },
    {
        "code": "16.02",
        "name": "Продажа элементов лесов",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "16",
        "pnl_article_name": "Выручка от продажи лесов",
        "pnl_impact": "income",
        "is_active": True,
    },
    {
        "code": "16.03",
        "name": "Продажа оборудования",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "16",
        "pnl_article_name": "Выручка от продажи оборудования",
        "pnl_impact": "income",
        "is_active": True,
    },
    {
        "code": "16.03.01",
        "name": "Продажа фанеры",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "16.03",
        "pnl_article_name": "Выручка от продажи материалов",
        "pnl_impact": "income",
        "is_active": True,
    },
    {
        "code": "16.03.02",
        "name": "Продажа Лом Бурк",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "16.03",
        "pnl_article_name": "Выручка от продажи материалов",
        "pnl_impact": "income",
        "is_active": True,
    },
    {
        "code": "16.04",
        "name": "Продажа автотранспорта",
        "movement_type": "inflow",
        "dds_section": "investing",
        "parent_code": "16",
        "pnl_article_name": "Прочие доходы (продажа ОС)",
        "pnl_impact": "income",
        "is_active": True,
    },
    {
        "code": "16.05",
        "name": "Прочие продажи",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "16",
        "pnl_article_name": "Прочие доходы",
        "pnl_impact": "income",
        "is_active": True,
    },
    {
        "code": "16.06",
        "name": "Прочие услуги",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "16",
        "pnl_article_name": "Выручка от прочих услуг",
        "pnl_impact": "income",
        "is_active": True,
    },
    # 17. Цессия (parent)
    {
        "code": "17",
        "name": "Цессия",
        "movement_type": "inflow",
        "dds_section": "operating",
        "is_pnl": True,
        "is_active": True,
    },
    {
        "code": "17.01",
        "name": "Цессия (уступка прав требования)",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "17",
        "pnl_article_name": "Прочие доходы (цессия)",
        "pnl_impact": "income",
        "is_active": True,
    },
    # 20. Финансовая деятельность (parent)
    {
        "code": "20",
        "name": "Финансовая деятельность",
        "movement_type": "inflow",
        "dds_section": "financing",
        "is_pnl": False,
        "is_active": True,
    },
    {
        "code": "20.01",
        "name": "Получение кредитов и займов",
        "movement_type": "inflow",
        "dds_section": "financing",
        "parent_code": "20",
        "pnl_impact": "none",
        "is_active": True,
    },
    {
        "code": "20.02",
        "name": "Возврат кредитов и займов",
        "movement_type": "outflow",
        "dds_section": "financing",
        "parent_code": "20",
        "pnl_impact": "none",
        "is_active": True,
    },
    {
        "code": "20.03",
        "name": "Проценты по кредитам и займам",
        "movement_type": "outflow",
        "dds_section": "operating",
        "parent_code": "20",
        "pnl_article_name": "Проценты по кредитам",
        "pnl_impact": "expense",
        "is_active": True,
    },
    {
        "code": "20.04",
        "name": "Вклады в уставный капитал",
        "movement_type": "inflow",
        "dds_section": "financing",
        "parent_code": "20",
        "pnl_impact": "none",
        "is_active": True,
    },
    {
        "code": "20.05",
        "name": "Выплата дивидендов",
        "movement_type": "outflow",
        "dds_section": "financing",
        "parent_code": "20",
        "pnl_impact": "none",
        "is_active": True,
    },
    # 30. Операционные расходы (parent)
    {
        "code": "30",
        "name": "Операционные расходы",
        "movement_type": "outflow",
        "dds_section": "operating",
        "is_pnl": True,
        "is_active": True,
    },
    {
        "code": "30.01",
        "name": "Закупка материалов (ремонт, обслуживание)",
        "movement_type": "outflow",
        "dds_section": "operating",
        "parent_code": "30",
        "pnl_article_name": "Материальные расходы",
        "pnl_impact": "expense",
        "is_active": True,
    },
    {
        "code": "30.02",
        "name": "Услуги связи (интернет, телефон)",
        "movement_type": "outflow",
        "dds_section": "operating",
        "parent_code": "30",
        "pnl_article_name": "Услуги связи",
        "pnl_impact": "expense",
        "is_active": True,
    },
    {
        "code": "30.03",
        "name": "Коммунальные платежи",
        "movement_type": "outflow",
        "dds_section": "operating",
        "parent_code": "30",
        "pnl_article_name": "Коммунальные расходы",
        "pnl_impact": "expense",
        "is_active": True,
    },
    {
        "code": "30.04",
        "name": "Аренда офиса и склада",
        "movement_type": "outflow",
        "dds_section": "operating",
        "parent_code": "30",
        "pnl_article_name": "Аренда",
        "pnl_impact": "expense",
        "is_active": True,
    },
    {
        "code": "30.05",
        "name": "Юридические и консультационные услуги",
        "movement_type": "outflow",
        "dds_section": "operating",
        "parent_code": "30",
        "pnl_article_name": "Юридические услуги",
        "pnl_impact": "expense",
        "is_active": True,
    },
    {
        "code": "30.06",
        "name": "Прочие услуги",
        "movement_type": "outflow",
        "dds_section": "operating",
        "parent_code": "30",
        "pnl_article_name": "Прочие расходы",
        "pnl_impact": "expense",
        "is_active": True,
    },
    # 31. Операции с недвижимостью (parent)
    {
        "code": "31",
        "name": "Операции с недвижимостью",
        "movement_type": "outflow",
        "dds_section": "investing",
        "is_pnl": False,
        "is_active": True,
    },
    {
        "code": "31.01",
        "name": "Приобретение зданий и сооружений",
        "movement_type": "outflow",
        "dds_section": "investing",
        "parent_code": "31",
        "pnl_impact": "none",
        "is_active": True,
    },
    {
        "code": "31.02",
        "name": "Продажа зданий и сооружений",
        "movement_type": "inflow",
        "dds_section": "investing",
        "parent_code": "31",
        "pnl_article_name": "Прочие доходы (продажа ОС)",
        "pnl_impact": "income",
        "is_active": True,
    },
    {
        "code": "31.03",
        "name": "Приобретение земельных участков",
        "movement_type": "outflow",
        "dds_section": "investing",
        "parent_code": "31",
        "pnl_impact": "none",
        "is_active": True,
    },
    {
        "code": "31.04",
        "name": "Продажа земельных участков",
        "movement_type": "inflow",
        "dds_section": "investing",
        "parent_code": "31",
        "pnl_article_name": "Прочие доходы (продажа ОС)",
        "pnl_impact": "income",
        "is_active": True,
    },
    # 32. Операции с оборудованием и ОС (parent)
    {
        "code": "32",
        "name": "Операции с оборудованием и ОС",
        "movement_type": "outflow",
        "dds_section": "investing",
        "is_pnl": False,
        "is_active": True,
    },
    {
        "code": "32.01",
        "name": "Приобретение оборудования (опалубка, леса)",
        "movement_type": "outflow",
        "dds_section": "investing",
        "parent_code": "32",
        "pnl_impact": "none",
        "is_active": True,
    },
    {
        "code": "32.02",
        "name": "Продажа оборудования",
        "movement_type": "inflow",
        "dds_section": "investing",
        "parent_code": "32",
        "pnl_article_name": "Прочие доходы (продажа ОС)",
        "pnl_impact": "income",
        "is_active": True,
    },
    # 33. Прочие инвестиции (parent)
    {
        "code": "33",
        "name": "Прочие инвестиции",
        "movement_type": "outflow",
        "dds_section": "investing",
        "is_pnl": False,
        "is_active": True,
    },
    {
        "code": "33.01",
        "name": "Приобретение финансовых вложений",
        "movement_type": "outflow",
        "dds_section": "investing",
        "parent_code": "33",
        "pnl_impact": "none",
        "is_active": True,
    },
    {
        "code": "33.02",
        "name": "Продажа финансовых вложений",
        "movement_type": "inflow",
        "dds_section": "investing",
        "parent_code": "33",
        "pnl_article_name": "Прочие доходы (финансовые вложения)",
        "pnl_impact": "income",
        "is_active": True,
    },
    # 40. Налоги и сборы (parent)
    {
        "code": "40",
        "name": "Налоги и сборы",
        "movement_type": "outflow",
        "dds_section": "operating",
        "is_pnl": True,
        "is_active": True,
    },
    {
        "code": "40.01",
        "name": "НДС (уплаченный)",
        "movement_type": "outflow",
        "dds_section": "operating",
        "parent_code": "40",
        "pnl_impact": "none",
        "is_active": True,
    },
    {
        "code": "40.02",
        "name": "Налог на прибыль",
        "movement_type": "outflow",
        "dds_section": "operating",
        "parent_code": "40",
        "pnl_article_name": "Налог на прибыль",
        "pnl_impact": "expense",
        "is_active": True,
    },
    {
        "code": "40.03",
        "name": "Страховые взносы",
        "movement_type": "outflow",
        "dds_section": "operating",
        "parent_code": "40",
        "pnl_article_name": "Страховые взносы",
        "pnl_impact": "expense",
        "is_active": True,
    },
    {
        "code": "40.04",
        "name": "НДФЛ",
        "movement_type": "outflow",
        "dds_section": "operating",
        "parent_code": "40",
        "pnl_impact": "none",
        "is_active": True,
    },
    {
        "code": "40.05",
        "name": "Налог на имущество",
        "movement_type": "outflow",
        "dds_section": "operating",
        "parent_code": "40",
        "pnl_article_name": "Налог на имущество",
        "pnl_impact": "expense",
        "is_active": True,
    },
    {
        "code": "40.06",
        "name": "Транспортный налог",
        "movement_type": "outflow",
        "dds_section": "operating",
        "parent_code": "40",
        "pnl_article_name": "Транспортный налог",
        "pnl_impact": "expense",
        "is_active": True,
    },
    {
        "code": "40.07",
        "name": "Земельный налог",
        "movement_type": "outflow",
        "dds_section": "operating",
        "parent_code": "40",
        "pnl_article_name": "Земельный налог",
        "pnl_impact": "expense",
        "is_active": True,
    },
    {
        "code": "40.08",
        "name": "Прочие налоги и сборы",
        "movement_type": "outflow",
        "dds_section": "operating",
        "parent_code": "40",
        "pnl_article_name": "Прочие налоги",
        "pnl_impact": "expense",
        "is_active": True,
    },
    # 50. Расчеты с персоналом (parent)
    {
        "code": "50",
        "name": "Расчеты с персоналом",
        "movement_type": "outflow",
        "dds_section": "operating",
        "is_pnl": False,
        "is_active": True,
    },
    {
        "code": "50.01",
        "name": "Выплата зарплаты",
        "movement_type": "outflow",
        "dds_section": "operating",
        "parent_code": "50",
        "pnl_article_name": "Расходы на оплату труда",
        "pnl_impact": "expense",
        "is_active": True,
    },
    {
        "code": "50.02",
        "name": "Аванс сотрудникам",
        "movement_type": "outflow",
        "dds_section": "operating",
        "parent_code": "50",
        "pnl_impact": "none",
        "is_active": True,
    },
    {
        "code": "50.03",
        "name": "Возврат от сотрудников",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "50",
        "pnl_impact": "none",
        "is_active": True,
    },
    {
        "code": "50.04",
        "name": "Выдача подотчетных средств",
        "movement_type": "outflow",
        "dds_section": "operating",
        "parent_code": "50",
        "pnl_impact": "none",
        "is_active": True,
    },
    {
        "code": "50.05",
        "name": "Возврат подотчетных средств",
        "movement_type": "inflow",
        "dds_section": "operating",
        "parent_code": "50",
        "pnl_impact": "none",
        "is_active": True,
    },
    # 70. Внутренние перемещения (parent)
    {
        "code": "70",
        "name": "Внутренние перемещения",
        "movement_type": "inflow",
        "dds_section": "internal",
        "is_pnl": False,
        "is_active": True,
    },
    {
        "code": "70.01",
        "name": "Перевод между счетами",
        "movement_type": "inflow",
        "dds_section": "internal",
        "parent_code": "70",
        "pnl_impact": "none",
        "is_active": True,
    },
    {
        "code": "70.02",
        "name": "Инкассация",
        "movement_type": "inflow",
        "dds_section": "internal",
        "parent_code": "70",
        "pnl_impact": "none",
        "is_active": True,
    },
]


async def main():
    async with async_session() as db:
        result = await db.execute(select(Category))
        existing = {c.code: c for c in result.scalars().all() if c.code}

        # First pass: create parents (no parent_code)
        for item in CATEGORIES:
            if item["code"] in existing:
                continue
            if item.get("parent_code"):
                continue

            cat = Category(
                code=item["code"],
                name=item["name"],
                type=CategoryType.income
                if item["movement_type"] == "inflow"
                else CategoryType.expense,
                movement_type=MovementType(item["movement_type"]),
                dds_section=DdsSection(item["dds_section"]),
                is_pnl=item.get("is_pnl", False),
                is_active=item.get("is_active", True),
            )
            db.add(cat)
            await db.flush()
            existing[item["code"]] = cat

        # Second pass: create children with parent_id and pnl_article
        for item in CATEGORIES:
            if item["code"] in existing:
                continue

            parent_code = item.get("parent_code")
            parent_id = (
                existing[parent_code].id
                if parent_code and parent_code in existing
                else None
            )

            pnl_article = None
            if item.get("pnl_article_name"):
                pnl_result = await db.execute(
                    select(Category).where(Category.name == item["pnl_article_name"])
                )
                pnl_article = pnl_result.scalar_one_or_none()
                if not pnl_article:
                    pnl_article = Category(
                        code=f"pnl_{item['code']}",
                        name=item["pnl_article_name"],
                        type=CategoryType.income
                        if item.get("pnl_impact") == "income"
                        else CategoryType.expense,
                        is_pnl=True,
                        is_active=True,
                    )
                    db.add(pnl_article)
                    await db.flush()

            cat = Category(
                code=item["code"],
                name=item["name"],
                type=CategoryType.income
                if item["movement_type"] == "inflow"
                else CategoryType.expense,
                movement_type=MovementType(item["movement_type"]),
                dds_section=DdsSection(item["dds_section"]),
                parent_id=parent_id,
                pnl_article_id=pnl_article.id if pnl_article else None,
                pnl_impact=PnlImpact(item.get("pnl_impact", "none")),
                is_pnl=item.get("is_pnl", False),
                is_active=item.get("is_active", True),
            )
            db.add(cat)
            await db.flush()
            existing[item["code"]] = cat

        await db.commit()
        print(f"Seeded {len(CATEGORIES)} DDS categories")


if __name__ == "__main__":
    from app.models import CategoryType

    asyncio.run(main())
