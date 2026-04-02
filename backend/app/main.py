from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import (
    auth,
    companies,
    accounts,
    categories,
    cost_centers,
    counterparties,
)
from app.routers import (
    transactions,
    bank_statements,
    categorization_rules,
    reports,
    employees,
    budget_items,
    payroll,
    currencies,
)

app = FastAPI(
    title="Management Accounting Service",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(accounts.router)
app.include_router(categories.router)
app.include_router(cost_centers.router)
app.include_router(counterparties.router)
app.include_router(transactions.router)
app.include_router(bank_statements.router)
app.include_router(categorization_rules.router)
app.include_router(reports.router)
app.include_router(employees.router)
app.include_router(budget_items.router)
app.include_router(payroll.router)
app.include_router(currencies.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
