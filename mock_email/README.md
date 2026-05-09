## mock_email

A tiny **mock email service** for local development and integration tests. It accepts “send email” requests, applies simple quota/rate-limit constraints, and returns deterministic responses (no real email is delivered).

### Goals / constraints

This service is intended to enforce **three limits**:

- **Burst**: max **10 requests / second**
- **Sustained**: max **100 requests / minute**
- **Daily**: max **10,000 messages / day**

Notes:
- Limits are intended to be enforced **per client** (typically by IP or an API key), and should be configurable later if needed.
- “Requests” and “messages” are treated equivalently here (1 request = 1 email message) unless you later add batching.

### Current status (in repo today)

- Implemented:
  - `GET /health` → returns a simple “ok” payload
- Not implemented yet (but this README defines the intended contract):
  - A “send email” endpoint (suggested below)
  - Rate limiting / quota enforcement (placeholder file `app/rate_limiter.py` is currently empty)
  - Containerization (the `Dockerfile` is currently empty)

### API

#### Health

`GET /health`

Response (example):

```json
{
  "status": "ok",
  "message": "Mock email service is running"
}
```

#### Send email (intended)

Suggested endpoint:

`POST /send`

Request body (example):

```json
{
  "to": ["user@example.com"],
  "subject": "Welcome!",
  "text": "Hello from the mock email service",
  "html": "<p>Hello from the mock email service</p>",
  "headers": {
    "X-Correlation-Id": "abc-123"
  }
}
```

Success response (example):

```json
{
  "status": "accepted",
  "message_id": "mock_01J0...etc",
  "accepted_at": "2026-05-09T10:00:00Z"
}
```

Rate limit responses (intended):

- **429 Too Many Requests** when burst/sustained limits are exceeded
- **403 Forbidden** (or **429**) when daily quota is exhausted

Error body (example):

```json
{
  "status": "rejected",
  "reason": "rate_limited",
  "limit": "10_req_per_sec",
  "retry_after_seconds": 1
}
```

### Running locally

This project uses FastAPI. From the repo root:

```bash
python -m uvicorn mock_email.app.main:app --reload --port 8001
```

Then verify:

```bash
curl -sS localhost:8001/health
```

### Integration notes

- **No delivery**: this service should never send real emails.
- **Deterministic behavior**: keep responses stable so tests don’t flake.
- **Observability (optional later)**: it’s often useful to log accepted/rejected sends with a correlation id and emit simple counters (accepted / rate_limited / daily_quota_exceeded).
