from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from src.models.department import Department
from src.models.employee import Employee
from src.schemas.employee import EmployeeCreate

class EmployeeService:
    @staticmethod
    async def create_employee(session: AsyncSession, department_id: int, schema: EmployeeCreate) -> Employee:
        dep_stmt = select(Department.id).where(Department.id == department_id)
        dep_exists = await session.execute(dep_stmt)
        if not dep_exists.scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Подразделение с id {department_id} не найдено"
            )
            
        new_employee = Employee(
            department_id=department_id,
            **schema.model_dump()
        )
        session.add(new_employee)
        await session.commit()
        await session.refresh(new_employee)
        return new_employee
