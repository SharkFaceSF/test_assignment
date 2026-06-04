from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field, BeforeValidator
from src.schemas.employee import EmployeeResponse


TrimmedStr = Annotated[
    str, 
    BeforeValidator(lambda v: v.strip() if isinstance(v, str) else v)
]

class DepartmentBase(BaseModel):
    name: TrimmedStr = Field(..., min_length=1, max_length=200, description="Название подразделения")

class DepartmentCreate(DepartmentBase):
    parent_id: int | None = Field(None, description="ID родительского подразделения")

class DepartmentUpdate(BaseModel):
    name: TrimmedStr | None = Field(None, min_length=1, max_length=200)
    parent_id: int | None = Field(None)

class DepartmentResponse(DepartmentBase):
    id: int
    parent_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True

class DepartmentTreeResponse(BaseModel):
    id: int
    name: str
    parent_id: int | None
    created_at: datetime
    
    employees: list[EmployeeResponse] = []
    children: list["DepartmentTreeResponse"] = []

    class Config:
        from_attributes = True
