from __future__ import annotations


class AppError(Exception):
    status_code: int = 500
    message: str = "An unexpected error occurred"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.__class__.message
        super().__init__(self.message)
