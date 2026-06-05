from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from src.models.department import Department
from src.models.employee import Employee
from src.schemas.department import DepartmentCreate, DepartmentUpdate

class DepartmentService:
    
    @staticmethod
    async def _check_name_uniqueness(session: AsyncSession, name: str, parent_id: int | None, exclude_id: int | None = None):
        """Проверяет уникальность имени департамента на одном уровне иерархии."""
        stmt = select(Department).where(Department.name == name, Department.parent_id == parent_id)
        if exclude_id:
            stmt = stmt.where(Department.id != exclude_id)
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Подразделение с именем '{name}' уже существует у данного родителя."
            )

    @staticmethod
    async def _is_cyclical(session: AsyncSession, current_id: int, new_parent_id: int | None) -> bool:
        """Рекурсивно проверяет, не пытаемся ли мы переместить департамент внутрь его собственного поддерева."""
        if new_parent_id is None:
            return False
        if current_id == new_parent_id:
            return True
            
        parent_id = new_parent_id
        while parent_id is not None:
            stmt = select(Department.parent_id).where(Department.id == parent_id)
            result = await session.execute(stmt)
            parent_id = result.scalar_one_or_none()
            
            if parent_id == current_id:
                return True
        return False

    @classmethod
    async def create_department(cls, session: AsyncSession, schema: DepartmentCreate) -> Department:
        if schema.parent_id:
            parent = await session.get(Department, schema.parent_id)
            if not parent:
                raise HTTPException(status_code=404, detail="Родительское подразделение не найдено")
                
        await cls._check_name_uniqueness(session, schema.name, schema.parent_id)
        
        new_dep = Department(**schema.model_dump())
        session.add(new_dep)
        await session.commit()
        await session.refresh(new_dep)
        return new_dep

    @classmethod
    async def update_department(cls, session: AsyncSession, dep_id: int, schema: DepartmentUpdate) -> Department:
        dep = await session.get(Department, dep_id)
        if not dep:
            raise HTTPException(status_code=404, detail="Подразделение не найдено")
            
        update_data = schema.model_dump(exclude_unset=True)
        
        new_parent_id = update_data.get("parent_id", dep.parent_id)
        new_name = update_data.get("name", dep.name)
        
        if "parent_id" in update_data:
            if await cls._is_cyclical(session, dep_id, new_parent_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Нельзя переместить подразделение внутрь самого себя или своего поддерева."
                )
                
        if "name" in update_data or "parent_id" in update_data:
            await cls._check_name_uniqueness(session, new_name, new_parent_id, exclude_id=dep_id)
            
        for key, value in update_data.items():
            setattr(dep, key, value)
            
        await session.commit()
        await session.refresh(dep)
        return dep

    @classmethod
    async def get_department_tree(cls, session: AsyncSession, dep_id: int, depth: int, include_employees: bool) -> dict:
        """Построение дерева с ограничением по глубине (depth)."""
        if depth < 1 or depth > 5:
            raise HTTPException(status_code=400, detail="Глубина (depth) должна быть от 1 до 5")
            
        dep = await session.get(Department, dep_id)
        if not dep:
            raise HTTPException(status_code=404, detail="Подразделение не найдено")

        async def _load_node(node_id: int, current_depth: int) -> dict:
            options = [selectinload(Department.employees)] if include_employees else []
            stmt = select(Department).where(Department.id == node_id).options(*options)
            res = await session.execute(stmt)
            current_node = res.scalar_one()
            
            employees_list = []
            if include_employees:
                employees_list = sorted(current_node.employees, key=lambda e: e.full_name)

            children_list = []
            if current_depth < depth:
                child_stmt = select(Department.id).where(Department.parent_id == node_id)
                child_res = await session.execute(child_stmt)
                child_ids = child_res.scalars().all()
                
                for c_id in child_ids:
                    children_list.append(await _load_node(c_id, current_depth + 1))

            return {
                "id": current_node.id,
                "name": current_node.name,
                "parent_id": current_node.parent_id,
                "created_at": current_node.created_at,
                "employees": employees_list,
                "children": children_list
            }

        return await _load_node(dep_id, 1)

    @classmethod
    async def delete_department(cls, session: AsyncSession, dep_id: int, mode: str, reassign_to_id: int | None):
        dep = await session.get(Department, dep_id)
        if not dep:
            raise HTTPException(status_code=404, detail="Подразделение не найдено")
            
        if mode == "cascade":
            await session.delete(dep)
        elif mode == "reassign":
            if not reassign_to_id:
                raise HTTPException(status_code=400, detail="reassign_to_department_id обязателен для режима reassign")
                
            target_dep = await session.get(Department, reassign_to_id)
            if not target_dep:
                raise HTTPException(status_code=404, detail="Целевое подразделение для перевода сотрудников не найдено")
                
            if reassign_to_id == dep_id:
                raise HTTPException(status_code=400, detail="Нельзя перевести сотрудников в удаляемое подразделение")

            await session.execute(
                update(Employee)
                .where(Employee.department_id == dep_id)
                .values(department_id=reassign_to_id)
            )
            
            await session.execute(
                update(Department)
                .where(Department.parent_id == dep_id)
                .values(parent_id=dep.parent_id)
            )
            
            await session.delete(dep)
        else:
            raise HTTPException(status_code=400, detail="Неверный режим удаления. Доступны: cascade, reassign")
            
        await session.commit()
