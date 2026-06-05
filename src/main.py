from fastapi import FastAPI
from src.routers.departments import router as department_router

app = FastAPI(
    title="API Организационной Структуры",
    version="1.0.0",
    description="Тестовое задание для управления подразделениями и сотрудниками"
)

app.include_router(department_router)

@app.get("/healthcheck", tags=["Health"])
async def health_check():
    return {"status": "ok"}
