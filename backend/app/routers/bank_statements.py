import hashlib
import io
import re
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
import pandas as pd
from app.dependencies import get_db
from app.models import BankStatement, BankStatementLine, CategorizationRule
from app.schemas import BankStatementLineOut, ProcessBankLine
from app.models import Transaction, TransactionType

router = APIRouter(prefix="/api/bank-statements", tags=["bank-statements"])


def _decode_text(file_bytes: bytes) -> str:
    for encoding in ["utf-8-sig", "utf-8", "cp1251", "windows-1251", "latin-1"]:
        try:
            return file_bytes.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    return file_bytes.decode("utf-8", errors="replace")


def _parse_csv(file_bytes: bytes) -> pd.DataFrame:
    text = _decode_text(file_bytes)
    lines = text.splitlines()

    header_line = lines[0]
    headers = header_line.split(";")

    data_rows = []
    for line in lines[1:]:
        if not line.strip():
            continue
        if line.startswith("Номер счета"):
            break
        parts = line.split(";")
        if len(parts) >= len(headers):
            data_rows.append(parts[: len(headers)])

    df = pd.DataFrame(data_rows, columns=headers)
    return _normalize_columns(df)


def _parse_xlsx(file_bytes: bytes) -> pd.DataFrame:
    df_all = pd.read_excel(io.BytesIO(file_bytes), header=None)

    header_row_idx = None
    for i, row in df_all.iterrows():
        if any("Дата" in str(v) for v in row if pd.notna(v)):
            header_row_idx = i
            break

    if header_row_idx is None:
        raise HTTPException(status_code=400, detail="Не найдена строка заголовков")

    df = pd.read_excel(io.BytesIO(file_bytes), header=header_row_idx)

    rows_to_keep = []
    for i in range(len(df)):
        if pd.notna(df.iloc[i].iloc[0]) and str(df.iloc[i].iloc[0]).startswith(
            "Номер счета"
        ):
            break
        rows_to_keep.append(i)

    df = df.iloc[rows_to_keep].reset_index(drop=True)
    return _normalize_columns(df)


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    col_map = {}
    for col in df.columns:
        cl = col.strip().lower()
        if cl in ("дата", "date", "дата платежа", "дата списания", "дата зачисления"):
            if "date" not in col_map.values():
                col_map[col] = "date"
        elif cl in ("сумма", "amount", "сумма платежа", "сумма списания"):
            if "amount" not in col_map.values():
                col_map[col] = "amount"
        elif cl in (
            "описание",
            "description",
            "назначение",
            "назначение платежа",
            "детали",
            "основание платежа",
        ):
            if "description" not in col_map.values():
                col_map[col] = "description"
        elif cl in (
            "контрагент",
            "counterparty",
            "получатель",
            "отправитель",
            "контрагент наименование",
            "наименование получателя",
            "наименование плательщика",
        ):
            if "counterparty_name" not in col_map.values():
                col_map[col] = "counterparty_name"

    df = df[list(col_map.keys())].rename(columns=col_map)

    required = {"date", "amount"}
    if not required.issubset(set(df.columns)):
        raise HTTPException(
            status_code=400,
            detail=f"Required columns: {required}, got: {set(df.columns)}",
        )

    df["date"] = pd.to_datetime(df["date"], dayfirst=True).dt.date
    df["amount"] = (
        df["amount"]
        .astype(str)
        .str.replace(",", ".")
        .str.replace(r"\s+", "", regex=True)
    )
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    if "description" not in df.columns:
        df["description"] = None
    if "counterparty_name" not in df.columns:
        df["counterparty_name"] = None

    df["counterparty_name"] = df["counterparty_name"].astype(str).str.strip()
    df["counterparty_name"] = df["counterparty_name"].str.replace('"', "")
    df["counterparty_name"] = df["counterparty_name"].replace("None", None)
    df["counterparty_name"] = df["counterparty_name"].replace("nan", None)

    df = df.dropna(subset=["date", "amount"])
    df = df[df["amount"] != 0]

    return df[["date", "amount", "description", "counterparty_name"]]


def _row_hash(date_val, amount, description) -> str:
    raw = f"{date_val}_{amount}_{description or ''}"
    return hashlib.md5(raw.encode()).hexdigest()


@router.post("/upload")
async def upload_statement(
    file: UploadFile = File(...),
    account_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    filename = file.filename or ""

    if filename.endswith(".csv"):
        df = _parse_csv(content)
    elif filename.endswith((".xlsx", ".xls")):
        df = _parse_xlsx(content)
    else:
        raise HTTPException(
            status_code=400, detail="Неподдерживаемый формат. Используйте CSV или XLSX."
        )

    statement = BankStatement(account_id=account_id)
    db.add(statement)
    await db.flush()

    existing_hashes = set()
    result = await db.execute(
        select(BankStatementLine).where(BankStatementLine.statement_id == statement.id)
    )
    for line in result.scalars().all():
        existing_hashes.add(_row_hash(line.date, line.amount, line.description))

    created = 0
    skipped = 0
    for _, row in df.iterrows():
        h = _row_hash(row["date"], row["amount"], row.get("description"))
        if h in existing_hashes:
            skipped += 1
            continue
        line = BankStatementLine(
            statement_id=statement.id,
            date=row["date"],
            amount=float(row["amount"]),
            description=row.get("description"),
            counterparty_name=row.get("counterparty_name"),
        )
        db.add(line)
        created += 1
        existing_hashes.add(h)

    await db.commit()
    return {"statement_id": statement.id, "created": created, "skipped": skipped}


@router.get("/{statement_id}/lines", response_model=list[BankStatementLineOut])
async def get_statement_lines(statement_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BankStatementLine)
        .where(BankStatementLine.statement_id == statement_id)
        .order_by(BankStatementLine.date)
    )
    return result.scalars().all()


@router.get("/unprocessed", response_model=list[BankStatementLineOut])
async def get_unprocessed_lines(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BankStatementLine)
        .where(BankStatementLine.is_processed == False)
        .order_by(BankStatementLine.date)
    )
    return result.scalars().all()


@router.get("/rules/auto-match")
async def auto_match_line(
    description: Optional[str] = None, db: AsyncSession = Depends(get_db)
):
    if not description:
        return {"category_id": None, "cost_center_id": None}
    result = await db.execute(select(CategorizationRule))
    rules = result.scalars().all()
    for rule in rules:
        if rule.keyword.lower() in description.lower():
            return {
                "category_id": rule.category_id,
                "cost_center_id": rule.cost_center_id,
            }
    return {"category_id": None, "cost_center_id": None}


@router.post("/lines/{line_id}/process")
async def process_line(
    line_id: int, data: ProcessBankLine, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(BankStatementLine)
        .options(joinedload(BankStatementLine.statement))
        .where(BankStatementLine.id == line_id)
    )
    line = result.scalar_one_or_none()
    if not line:
        raise HTTPException(status_code=404, detail="Строка не найдена")
    if line.is_processed:
        raise HTTPException(status_code=400, detail="Строка уже обработана")

    tx_type = TransactionType.income if line.amount > 0 else TransactionType.expense
    tx = Transaction(
        date=line.date,
        amount=abs(line.amount),
        type=tx_type,
        account_id=line.statement.account_id if line.statement else 1,
        category_id=data.category_id,
        cost_center_id=data.cost_center_id,
        counterparty_id=data.counterparty_id,
        comment=data.comment or line.description,
    )
    db.add(tx)
    await db.flush()
    line.is_processed = True
    line.transaction_id = tx.id
    await db.commit()
    return {"transaction_id": tx.id}


@router.post("/lines/batch-process")
async def batch_process_lines(line_ids: list[int], db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BankStatementLine)
        .options(joinedload(BankStatementLine.statement))
        .where(BankStatementLine.id.in_(line_ids))
    )
    lines = result.scalars().all()
    processed = 0
    for line in lines:
        if line.is_processed:
            continue
        result_rules = await db.execute(select(CategorizationRule))
        rules = result_rules.scalars().all()
        category_id = None
        cost_center_id = None
        if line.description:
            for rule in rules:
                if rule.keyword.lower() in (line.description or "").lower():
                    category_id = rule.category_id
                    cost_center_id = rule.cost_center_id
                    break
        tx_type = TransactionType.income if line.amount > 0 else TransactionType.expense
        tx = Transaction(
            date=line.date,
            amount=abs(line.amount),
            type=tx_type,
            account_id=line.statement.account_id if line.statement else 1,
            category_id=category_id,
            cost_center_id=cost_center_id,
            comment=line.description,
        )
        db.add(tx)
        await db.flush()
        line.is_processed = True
        line.transaction_id = tx.id
        processed += 1
    await db.commit()
    return {"processed": processed}
