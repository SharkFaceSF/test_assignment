from datetime import datetime, date
from typing import Annotated
from pydantic import BaseModel, Field, BeforeValidator


TrimmedStr = Annotated[
    str, 
    BeforeValidator(lambda v: v.strip() if isinstance(v, str) else v)
]

class EmployeeBase(BaseModel):
    full_name: TrimmedStr = Field(..., min_length=1, max_length=200, description="ФИО сотрудника")
    position: TrimmedStr = Field(..., min_length=1, max_length=200, description="Должность")
    hired_at: date | None = Field(None, description="Дата найма")

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    id: int
    department_id: int
    created_at: datetime

    class Config:
        from_attributes = True
