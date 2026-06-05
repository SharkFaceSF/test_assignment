import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_create_department_success():
    """Проверяет успешное создание департамента"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/departments/", 
            json={"name": "Backend Team", "parent_id": None}
        )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Backend Team"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_department_empty_name_error():
    """Проверяет, что пустые имена или имена из пробелов возвращают ошибку 422"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/departments/", 
            json={"name": "   ", "parent_id": None}
        )
    assert response.status_code == 422
