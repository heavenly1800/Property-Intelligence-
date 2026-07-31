import asyncio
import hashlib
import json
import threading
import time
from dataclasses import dataclass
from fastapi import HTTPException, Request
from app.core.settings import get_settings

@dataclass
class StoredResult:
    fingerprint: str
    result: object
    expires_at: float

class InMemoryRateLimiter:
    def __init__(self):
        self._events: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def check(self, key: str, limit: int, window: int) -> None:
        now = time.monotonic()
        with self._lock:
            events = [stamp for stamp in self._events.get(key, []) if now - stamp < window]
            if len(events) >= limit:
                retry = max(1, int(window - (now - events[0])))
                raise HTTPException(429, "Too many requests.", headers={"Retry-After": str(retry)})
            events.append(now)
            self._events[key] = events

class InMemoryIdempotencyStore:
    def __init__(self):
        self._items: dict[str, StoredResult] = {}
        self._lock = threading.Lock()
        self._async_locks: dict[str, asyncio.Lock] = {}

    def run(self, namespace: str, key: str, payload: object, operation):
        now = time.monotonic()
        fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str, separators=(",", ":")).encode()).hexdigest()
        storage_key = f"{namespace}:{key}"
        with self._lock:
            item = self._items.get(storage_key)
            if item and item.expires_at > now:
                if item.fingerprint != fingerprint:
                    raise HTTPException(409, "Idempotency-Key was already used with a different request.")
                return item.result
            self._items.pop(storage_key, None)
            result = operation()
            self._items[storage_key] = StoredResult(fingerprint, result, now + get_settings().IDEMPOTENCY_RETENTION_SECONDS)
        return result

    async def run_async(self, namespace: str, key: str, payload: object, operation):
        now = time.monotonic()
        fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str, separators=(",", ":")).encode()).hexdigest()
        storage_key = f"{namespace}:{key}"
        with self._lock:
            operation_lock = self._async_locks.setdefault(storage_key, asyncio.Lock())
        async with operation_lock:
            with self._lock:
                item = self._items.get(storage_key)
                if item and item.expires_at > time.monotonic():
                    if item.fingerprint != fingerprint:
                        raise HTTPException(409, "Idempotency-Key was already used with a different request.")
                    return item.result
                self._items.pop(storage_key, None)
            result = await operation()
            with self._lock:
                self._items[storage_key] = StoredResult(fingerprint, result, time.monotonic() + get_settings().IDEMPOTENCY_RETENTION_SECONDS)
            return result

rate_limiter = InMemoryRateLimiter()
idempotency_store = InMemoryIdempotencyStore()

def protected_operation(request: Request, namespace: str, payload: object, operation):
    settings = get_settings()
    identity = getattr(request.state, "user_id", None) or (request.client.host if request.client else "unknown")
    if settings.RATE_LIMIT_ENABLED:
        rate_limiter.check(f"{namespace}:{identity}", settings.RATE_LIMIT_REQUESTS, settings.RATE_LIMIT_WINDOW_SECONDS)
    key = request.headers.get("Idempotency-Key")
    if not key:
        return operation()
    if len(key) > 200:
        raise HTTPException(400, "Idempotency-Key is too long.")
    return idempotency_store.run(f"{identity}:{namespace}", key, payload, operation)

async def protected_operation_async(request: Request, namespace: str, payload: object, operation):
    settings = get_settings()
    identity = getattr(request.state, "user_id", None) or (request.client.host if request.client else "unknown")
    if settings.RATE_LIMIT_ENABLED:
        rate_limiter.check(f"{namespace}:{identity}", settings.RATE_LIMIT_REQUESTS, settings.RATE_LIMIT_WINDOW_SECONDS)
    key = request.headers.get("Idempotency-Key")
    if not key:
        return await operation()
    if len(key) > 200:
        raise HTTPException(400, "Idempotency-Key is too long.")
    return await idempotency_store.run_async(f"{identity}:{namespace}", key, payload, operation)
