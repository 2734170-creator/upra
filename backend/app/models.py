from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    Boolean,
    ForeignKey,
    DateTime,
    Enum as SAEnum,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func
import enum


class Base(DeclarativeBase):
    pass


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class CompanyType(str, enum.Enum):
    ooo = "ooo"
    ip = "ip"


class AccountType(str, enum.Enum):
    bank = "bank"
    cash = "cash"


class CategoryType(str, enum.Enum):
    income = "income"
    expense = "expense"


class CounterpartyType(str, enum.Enum):
    client = "client"
    supplier = "supplier"


class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"
    transfer = "transfer"


class PayrollStatus(str, enum.Enum):
    accrued = "accrued"
    paid = "paid"


class Currency(Base):
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False)
    numeric_code = Column(String(3), nullable=False)
    name_ru = Column(String(50), nullable=False)
    symbol = Column(String(5), nullable=False)

    companies = relationship("Company", back_populates="currency_rel")
    accounts = relationship("Account", back_populates="currency_rel")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.user)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(SAEnum(CompanyType), nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)

    currency_rel = relationship("Currency", back_populates="companies")
    accounts = relationship("Account", back_populates="company")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    type = Column(SAEnum(AccountType), nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)

    company = relationship("Company", back_populates="accounts")
    currency_rel = relationship("Currency", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")
    bank_statements = relationship("BankStatement", back_populates="account")


class MovementType(str, enum.Enum):
    inflow = "inflow"
    outflow = "outflow"


class DdsSection(str, enum.Enum):
    operating = "operating"
    investing = "investing"
    financing = "financing"
    internal = "internal"


class PnlImpact(str, enum.Enum):
    income = "income"
    expense = "expense"
    none = "none"


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(SAEnum(CategoryType), nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    is_pnl = Column(Boolean, default=False)
    code = Column(String(20), nullable=True)
    movement_type = Column(SAEnum(MovementType), nullable=True)
    dds_section = Column(SAEnum(DdsSection), nullable=True)
    pnl_article_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    pnl_impact = Column(SAEnum(PnlImpact), nullable=True)
    is_active = Column(Boolean, default=True)
    comment = Column(Text, nullable=True)

    parent = relationship(
        "Category", remote_side=[id], foreign_keys=[parent_id], backref="children"
    )
    pnl_article = relationship(
        "Category", remote_side=[id], foreign_keys=[pnl_article_id]
    )
    transactions = relationship("Transaction", back_populates="category")
    budget_items = relationship("BudgetItem", back_populates="category")
    rules = relationship("CategorizationRule", back_populates="category")


class CostCenter(Base):
    __tablename__ = "cost_centers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("cost_centers.id"), nullable=True)

    parent = relationship("CostCenter", remote_side=[id], backref="children")
    transactions = relationship("Transaction", back_populates="cost_center")
    employees = relationship("Employee", back_populates="cost_center")
    budget_items = relationship("BudgetItem", back_populates="cost_center")


class Counterparty(Base):
    __tablename__ = "counterparties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(SAEnum(CounterpartyType), nullable=False)

    transactions = relationship("Transaction", back_populates="counterparty")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(SAEnum(TransactionType), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    cost_center_id = Column(Integer, ForeignKey("cost_centers.id"), nullable=True)
    counterparty_id = Column(Integer, ForeignKey("counterparties.id"), nullable=True)
    comment = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    cost_center = relationship("CostCenter", back_populates="transactions")
    counterparty = relationship("Counterparty", back_populates="transactions")
    pnl_entries = relationship("PnlEntry", back_populates="transaction")


class PnlEntry(Base):
    __tablename__ = "pnl_entries"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    impact = Column(SAEnum(PnlImpact), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    transaction = relationship("Transaction", back_populates="pnl_entries")
    category = relationship("Category")


class BudgetItem(Base):
    __tablename__ = "budget_items"

    id = Column(Integer, primary_key=True, index=True)
    period = Column(Date, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    cost_center_id = Column(Integer, ForeignKey("cost_centers.id"), nullable=True)
    amount = Column(Float, nullable=False)

    category = relationship("Category", back_populates="budget_items")
    cost_center = relationship("CostCenter", back_populates="budget_items")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    cost_center_id = Column(Integer, ForeignKey("cost_centers.id"), nullable=True)
    base_salary = Column(Float, nullable=False, default=0)

    cost_center = relationship("CostCenter", back_populates="employees")
    payroll_accruals = relationship("PayrollAccrual", back_populates="employee")


class PayrollAccrual(Base):
    __tablename__ = "payroll_accruals"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    period = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(
        SAEnum(PayrollStatus), nullable=False, default=PayrollStatus.accrued
    )

    employee = relationship("Employee", back_populates="payroll_accruals")


class BankStatement(Base):
    __tablename__ = "bank_statements"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    account = relationship("Account", back_populates="bank_statements")
    lines = relationship("BankStatementLine", back_populates="statement")


class BankStatementLine(Base):
    __tablename__ = "bank_statement_lines"

    id = Column(Integer, primary_key=True, index=True)
    statement_id = Column(Integer, ForeignKey("bank_statements.id"), nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(1000), nullable=True)
    counterparty_name = Column(String(255), nullable=True)
    is_processed = Column(Boolean, default=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)

    statement = relationship("BankStatement", back_populates="lines")
    transaction = relationship("Transaction")


class CategorizationRule(Base):
    __tablename__ = "categorization_rules"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    cost_center_id = Column(Integer, ForeignKey("cost_centers.id"), nullable=True)

    category = relationship("Category", back_populates="rules")
    cost_center = relationship("CostCenter")
