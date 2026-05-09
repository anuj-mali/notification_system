from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class SendEmailRequest(BaseModel):
    to: list[EmailStr]
    subject: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1, max_length=10000)

    idempotency_key: UUID | None = None


class SendEmailResponse(BaseModel):
    message_id: UUID
    status: str = "accepted"
    accepted_at: datetime
