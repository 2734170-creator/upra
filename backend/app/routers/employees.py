from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.models import Employee
from app.schemas import EmployeeCreate, EmployeeOut

router = APIRouter(prefix="/api/employees", tags=["employees"])


@router.get("", response_model=list[EmployeeOut])
async def list_employees(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Employee))
    return result.scalars().all()


@router.post("", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
async def create_employee(data: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    emp = Employee(**data.model_dump())
    db.add(emp)
    await db.commit()
    await db.refresh(emp)
    return emp


@router.get("/{emp_id}", response_model=EmployeeOut)
async def get_employee(emp_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Employee).where(Employee.id == emp_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


@router.put("/{emp_id}", response_model=EmployeeOut)
async def update_employee(
    emp_id: int, data: EmployeeCreate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Employee).where(Employee.id == emp_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    for key, value in data.model_dump().items():
        setattr(emp, key, value)
    await db.commit()
    await db.refresh(emp)
    return emp


@router.delete("/{emp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(emp_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Employee).where(Employee.id == emp_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    await db.delete(emp)
    await db.commit()
