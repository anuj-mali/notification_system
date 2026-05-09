from fastapi import FastAPI, status, Request, Depends
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError
from app.core.config import config

from app.schemas import SendEmailRequest, SendEmailResponse
from app.provider import get_provider, MockEmailProvider
from app.rate_limiter import get_rate_limiter, RateLimiter

app = FastAPI(
    title="Mock Email Service",
    description="A mock email service for testing and development",
    docs_url="/docs" if config.debug else None,
    redoc_url="/redoc" if config.debug else None,
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    headers = (
        {"Retry-After": str(exc.retry_after)} if hasattr(exc, "retry_after") else {}
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.message},
        headers=headers,
    )


@app.get("/health")
async def health():
    return {"status": "ok", "message": "Mock email service is running"}


@app.post("/send", status_code=status.HTTP_202_ACCEPTED)
async def send(
    request: SendEmailRequest,
    provider: MockEmailProvider = Depends(get_provider),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
) -> SendEmailResponse:
    await rate_limiter.check()
    response = await provider.send(request.to, request.subject, request.body)
    return SendEmailResponse(**response)
