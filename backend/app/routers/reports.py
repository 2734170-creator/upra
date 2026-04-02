from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date
from app.dependencies import get_db
from app.models import Transaction, Category, BudgetItem as BudgetItemModel
from app.models import TransactionType
from app.schemas import (
    CashflowReport,
    CashflowReportItem,
    PnlReport,
    PnlReportItem,
    BudgetReport,
    BudgetVsFactItem,
)

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/cashflow", response_model=CashflowReport)
async def cashflow_report(
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Transaction, Category.name.label("category_name"))
        .join(Category, Transaction.category_id == Category.id, isouter=True)
        .where(Transaction.date >= date_from, Transaction.date <= date_to)
        .order_by(Category.name)
    )
    rows = result.all()

    grouped = {}
    for tx, cat_name in rows:
        cid = tx.category_id or 0
        cname = cat_name or "Без категории"
        if cid not in grouped:
            grouped[cid] = {"name": cname, "income": 0.0, "expense": 0.0}
        if tx.type.value == "income":
            grouped[cid]["income"] += tx.amount
        elif tx.type.value == "expense":
            grouped[cid]["expense"] += tx.amount

    items = [
        CashflowReportItem(
            category_id=cid,
            category_name=v["name"],
            income=round(v["income"], 2),
            expense=round(v["expense"], 2),
            net=round(v["income"] - v["expense"], 2),
        )
        for cid, v in grouped.items()
    ]

    opening = 0.0
    total_net = sum(i.net for i in items)
    closing = opening + total_net

    return CashflowReport(
        period_start=date_from,
        period_end=date_to,
        items=items,
        opening_balance=opening,
        closing_balance=round(closing, 2),
    )


@router.get("/pnl", response_model=PnlReport)
async def pnl_report(
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(
            Transaction,
            Category.name.label("category_name"),
        )
        .join(Category, Transaction.category_id == Category.id)
        .where(
            Transaction.date >= date_from,
            Transaction.date <= date_to,
            Category.is_pnl == True,
        )
    )
    rows = result.all()

    total_income = 0.0
    total_expense = 0.0
    items = []

    grouped = {}
    for tx, cat_name in rows:
        key = (tx.category_id or 0, tx.cost_center_id)
        if key not in grouped:
            grouped[key] = {
                "cat_name": cat_name,
                "cc_id": tx.cost_center_id,
                "amount": 0.0,
            }
        grouped[key]["amount"] += tx.amount if tx.type.value == "income" else -tx.amount

    for (cid, ccid), v in grouped.items():
        amt = round(v["amount"], 2)
        if amt > 0:
            total_income += amt
        else:
            total_expense += abs(amt)
        items.append(
            PnlReportItem(
                category_id=cid,
                category_name=v["cat_name"],
                cost_center_id=ccid,
                cost_center_name=None,
                amount=amt,
            )
        )

    return PnlReport(
        period_start=date_from,
        period_end=date_to,
        income=round(total_income, 2),
        expense=round(total_expense, 2),
        profit=round(total_income - total_expense, 2),
        items=items,
    )


@router.get("/budget", response_model=BudgetReport)
async def budget_report(
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: AsyncSession = Depends(get_db),
):
    budgets_result = await db.execute(
        select(BudgetItemModel).where(
            BudgetItemModel.period >= date_from, BudgetItemModel.period <= date_to
        )
    )
    budgets = budgets_result.scalars().all()

    items = []
    for budget in budgets:
        actual_result = await db.execute(
            select(func.sum(Transaction.amount)).where(
                Transaction.category_id == budget.category_id,
                Transaction.cost_center_id == budget.cost_center_id,
                Transaction.date >= date_from,
                Transaction.date <= date_to,
                Transaction.type == TransactionType.expense,
            )
        )
        actual = actual_result.scalar() or 0.0
        deviation = budget.amount - actual
        pct = (deviation / budget.amount * 100) if budget.amount else 0.0

        items.append(
            BudgetVsFactItem(
                category_id=budget.category_id,
                category_name="",
                cost_center_id=budget.cost_center_id,
                cost_center_name=None,
                planned=budget.amount,
                actual=round(actual, 2),
                deviation=round(deviation, 2),
                deviation_pct=round(pct, 2),
            )
        )

    return BudgetReport(
        period_start=date_from,
        period_end=date_to,
        items=items,
    )
