from fastapi import FastAPI

app = FastAPI(
    title="API Организационной Структуры",
    version="1.0.0",
    description="Тестовое задание для управления подразделениями и сотрудниками"
)

@app.get("/healthcheck", tags=["Health"])
async def health_check():
    return {"status": "ok"}
