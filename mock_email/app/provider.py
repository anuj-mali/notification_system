from __future__ import annotations

import uuid
from typing import Any
from pydantic import EmailStr

from datetime import datetime


class MockEmailProvider:
    async def send(self, to: list[EmailStr], subject: str, body: str) -> dict[str, Any]:
        return {
            "message_id": str(uuid.uuid4()),
            "status": "accepted",
            "accepted_at": datetime.now(),
        }


def get_provider() -> MockEmailProvider:
    return MockEmailProvider()
