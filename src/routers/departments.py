from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentTreeResponse,
    DepartmentUpdate,
    EmployeeResponse,
    EmployeeCreate
)
from src.services.department_service import DepartmentService
from src.services.employee_service import EmployeeService

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.post(
    "/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED
)
async def create_department(
    schema: DepartmentCreate, db: AsyncSession = Depends(get_db)
):
    return await DepartmentService.create_department(db, schema)


@router.post(
    "/{id}/employees/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_employee(
    id: int, schema: EmployeeCreate, db: AsyncSession = Depends(get_db)
):
    return await EmployeeService.create_employee(db, id, schema)


@router.get("/{id}", response_model=DepartmentTreeResponse)
async def get_department(
    id: int,
    depth: int = Query(1, ge=1, le=5),
    include_employees: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    return await DepartmentService.get_department_tree(
        db, id, depth, include_employees
    )


@router.patch("/{id}", response_model=DepartmentResponse)
async def update_department(
    id: int, schema: DepartmentUpdate, db: AsyncSession = Depends(get_db)
):
    return await DepartmentService.update_department(db, id, schema)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    id: int,
    mode: str = Query(..., description="cascade | reassign"),
    reassign_to_department_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    await DepartmentService.delete_department(
        db, id, mode, reassign_to_department_id
    )
    return None
