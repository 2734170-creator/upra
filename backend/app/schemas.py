from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional
from app.models import (
    UserRole,
    CompanyType,
    AccountType,
    CategoryType,
    CounterpartyType,
    TransactionType,
    PayrollStatus,
)


class Token(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    email: str
    password: str
    role: UserRole = UserRole.user


class UserOut(BaseModel):
    id: int
    email: str
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class CurrencyCreate(BaseModel):
    name_ru: str
    symbol: str = ""
    code: str = ""
    numeric_code: str = ""


class CurrencyOut(BaseModel):
    id: int
    code: str
    numeric_code: str
    name_ru: str
    symbol: str

    class Config:
        from_attributes = True


class CompanyCreate(BaseModel):
    name: str
    type: CompanyType
    currency_id: Optional[int] = None


class CompanyOut(BaseModel):
    id: int
    name: str
    type: CompanyType
    currency_id: Optional[int] = None
    currency_code: Optional[str] = None

    class Config:
        from_attributes = True


class AccountCreate(BaseModel):
    name: str
    company_id: int
    type: AccountType
    currency_id: Optional[int] = None


class AccountOut(BaseModel):
    id: int
    name: str
    company_id: int
    type: AccountType
    currency_id: Optional[int] = None
    currency_code: Optional[str] = None

    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    name: str
    type: CategoryType
    parent_id: Optional[int] = None
    is_pnl: bool = False


class CategoryOut(BaseModel):
    id: int
    name: str
    type: CategoryType
    parent_id: Optional[int]
    is_pnl: bool

    class Config:
        from_attributes = True


class CostCenterCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None


class CostCenterOut(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]

    class Config:
        from_attributes = True


class CounterpartyCreate(BaseModel):
    name: str
    type: CounterpartyType


class CounterpartyOut(BaseModel):
    id: int
    name: str
    type: CounterpartyType

    class Config:
        from_attributes = True


class TransactionCreate(BaseModel):
    date: date
    amount: float
    type: TransactionType
    account_id: int
    category_id: Optional[int] = None
    cost_center_id: Optional[int] = None
    counterparty_id: Optional[int] = None
    comment: Optional[str] = None


class TransactionUpdate(BaseModel):
    date: Optional[date] = None
    amount: Optional[float] = None
    type: Optional[TransactionType] = None
    account_id: Optional[int] = None
    category_id: Optional[int] = None
    cost_center_id: Optional[int] = None
    counterparty_id: Optional[int] = None
    comment: Optional[str] = None


class TransactionOut(BaseModel):
    id: int
    date: date
    amount: float
    type: TransactionType
    account_id: int
    category_id: Optional[int]
    cost_center_id: Optional[int]
    counterparty_id: Optional[int]
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class BudgetItemCreate(BaseModel):
    period: date
    category_id: int
    cost_center_id: Optional[int] = None
    amount: float


class BudgetItemOut(BaseModel):
    id: int
    period: date
    category_id: int
    cost_center_id: Optional[int]
    amount: float

    class Config:
        from_attributes = True


class EmployeeCreate(BaseModel):
    name: str
    cost_center_id: Optional[int] = None
    base_salary: float = 0


class EmployeeOut(BaseModel):
    id: int
    name: str
    cost_center_id: Optional[int]
    base_salary: float

    class Config:
        from_attributes = True


class PayrollAccrualCreate(BaseModel):
    employee_id: int
    period: date
    amount: float
    status: PayrollStatus = PayrollStatus.accrued


class PayrollAccrualOut(BaseModel):
    id: int
    employee_id: int
    period: date
    amount: float
    status: PayrollStatus

    class Config:
        from_attributes = True


class BankStatementLineOut(BaseModel):
    id: int
    statement_id: int
    date: date
    amount: float
    description: Optional[str]
    counterparty_name: Optional[str]
    is_processed: bool
    transaction_id: Optional[int]

    class Config:
        from_attributes = True


class CategorizationRuleCreate(BaseModel):
    keyword: str
    category_id: int
    cost_center_id: Optional[int] = None


class CategorizationRuleOut(BaseModel):
    id: int
    keyword: str
    category_id: int
    cost_center_id: Optional[int]

    class Config:
        from_attributes = True


class ProcessBankLine(BaseModel):
    category_id: Optional[int] = None
    cost_center_id: Optional[int] = None
    counterparty_id: Optional[int] = None
    comment: Optional[str] = None


class CashflowReportItem(BaseModel):
    category_id: int
    category_name: str
    income: float
    expense: float
    net: float


class CashflowReport(BaseModel):
    period_start: date
    period_end: date
    items: list[CashflowReportItem]
    opening_balance: float
    closing_balance: float


class PnlReportItem(BaseModel):
    category_id: int
    category_name: str
    cost_center_id: Optional[int]
    cost_center_name: Optional[str]
    amount: float


class PnlReport(BaseModel):
    period_start: date
    period_end: date
    income: float
    expense: float
    profit: float
    items: list[PnlReportItem]


class BudgetVsFactItem(BaseModel):
    category_id: int
    category_name: str
    cost_center_id: Optional[int]
    cost_center_name: Optional[str]
    planned: float
    actual: float
    deviation: float
    deviation_pct: float


class BudgetReport(BaseModel):
    period_start: date
    period_end: date
    items: list[BudgetVsFactItem]
