## mock_email

A tiny **mock email service** for local development and integration tests. It accepts "send email" requests, applies a simple in-memory rate limit, and returns accepted responses without delivering real email.

### Current status

Implemented:

- `GET /health` returns a simple health payload.
- `POST /send` accepts a mock email request and returns `202 Accepted`.
- Basic in-memory token-bucket rate limiting is applied before accepting a send.

Not implemented:

- Real email delivery.
- Daily quotas.
- Per-client or per-API-key rate limits.
- Distributed/shared rate limiting across workers or service instances.
- Server-side idempotency handling.
- Containerization; `Dockerfile` is currently empty.

### Rate limits

The current limiter is configured from `EMAIL__REQUEST_PER_MINUTE` and `EMAIL__BURST_PER_SECOND`, with defaults of:

- **Burst capacity**: `10`
- **Refill rate**: `100 / minute`

Important limitations:

- The limiter is process-local and stored in memory.
- The limiter is global for the whole service, not scoped by IP address, user, tenant, or API key.
- Limits reset when the process restarts.
- Multiple Uvicorn/Gunicorn workers would each have their own independent limiter.
- It uses a token-bucket approximation, not a sliding window log.
- Daily quota enforcement is not implemented.
- `Retry-After` is currently a fixed value from the error type, not a precise wait time from the bucket state.
- One request is treated as one message, regardless of recipient count.

### Future direction

Planned improvements:

- Add daily quotas, for example `10,000` accepted messages per day.
- Replace or supplement the current token bucket with a sliding window log algorithm.
- Move rate-limit state to Redis so limits are shared across workers and instances.
- Enforce rate limits per API key.
- Keep API keys mock-only: callers can provide arbitrary UUIDs or random strings. No API key generation or management logic is required for this service.

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

`POST /send`

Request body (example):

```json
{
  "to": ["user@example.com"],
  "subject": "Welcome!",
  "body": "Hello from the mock email service",
  "idempotency_key": "8abf9d35-bb8c-4c54-9de0-c3d67fd56b0d"
}
```

`idempotency_key` is accepted as client-owned metadata only. The mock email service does not de-duplicate requests, replay previous responses, or enforce idempotency. Clients that need idempotent behavior should store and enforce it on their side.

Success response (example):

```json
{
  "status": "accepted",
  "message_id": "8e417e91-eeec-4771-a35d-e7416e6ca8c2",
  "accepted_at": "2026-05-09T10:00:00Z"
}
```

Rate limit responses:

- **429 Too Many Requests** when the current token bucket is exhausted.

Error body (example):

```json
{
  "status": "error",
  "message": "Rate limit exceeded"
}
```

The response also includes a `Retry-After` header.

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
- **Client-owned idempotency**: callers are responsible for de-duplicating retries if their workflow requires it.
- **Mock API keys later**: when per-key limits are added, use caller-supplied UUIDs or random strings as API keys.
- **Observability (optional later)**: it’s often useful to log accepted/rejected sends with a correlation id and emit simple counters (accepted / rate_limited / daily_quota_exceeded).
