from __future__ import annotations


class AppError(Exception):
    status_code: int = 500
    message: str = "An unexpected error occurred"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.__class__.message
        super().__init__(self.message)


class RateLimitExceededError(AppError):
    status_code: int = 429
    message: str = "Rate limit exceeded"
    retry_after: int = 30


class InvalidIdempotencyKeyError(AppError):
    status_code: int = 400
    message: str = "Invalid idempotency key"
