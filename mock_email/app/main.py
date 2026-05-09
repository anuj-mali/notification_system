from fastapi import FastAPI

from app.core.config import config

app = FastAPI(
    title="Mock Email Service",
    description="A mock email service for testing and development",
    docs_url="/docs" if config.debug else None,
    redoc_url="/redoc" if config.debug else None,
)


@app.get("/health")
async def health():
    return {"status": "ok", "message": "Mock email service is running"}
