"""Transactional outbox, bounded retries, HMAC delivery and durable receiver deduplication."""

import hashlib
import hmac
import json
import tempfile
import time
import uuid
from pathlib import Path
import httpx
from sqlalchemy import String, Float, select, update
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base, database


class Event(Base):
    __tablename__ = "outbox"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    payload: Mapped[str]
    state: Mapped[str]
    attempts: Mapped[int]
    next_at: Mapped[float] = mapped_column(Float)
    lease: Mapped[str | None]
    error: Mapped[str | None]


class Receipt(Base):
    __tablename__ = "receipts"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    payload_hash: Mapped[str]
    body: Mapped[str]


def sign(secret, timestamp, event_id, body):
    return hmac.new(secret.encode(), f"{timestamp}.{event_id}.".encode() + body, hashlib.sha256).hexdigest()


class DeliveryEngine:
    def __init__(self, url=None):
        self.engine, self.sessions = database(url)

    def enqueue(self, event_id, payload):
        body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        with self.sessions.begin() as s:
            old = s.get(Event, event_id)
            if old:
                if old.payload != body:
                    raise ValueError("event ID reused for another payload")
                return old.id
            s.add(
                Event(
                    id=event_id, payload=body, state="pending", attempts=0, next_at=0, lease=None, error=None
                )
            )
        return event_id

    def deliver(self, send, secret, now=None, max_attempts=4):
        now = time.time() if now is None else now
        token = str(uuid.uuid4())
        with self.sessions.begin() as s:
            event = s.scalar(
                select(Event)
                .where(Event.state.in_(["pending", "retry", "sending"]), Event.next_at <= now)
                .order_by(Event.next_at, Event.id)
                .with_for_update(skip_locked=True)
            )
            if not event:
                return None
            claimed = s.execute(
                update(Event)
                .where(Event.id == event.id, Event.state == event.state, Event.next_at == event.next_at)
                .values(state="sending", lease=token, next_at=now + 30, attempts=event.attempts + 1)
            )
            if claimed.rowcount != 1:
                return None
            eid, body, attempt = event.id, event.payload.encode(), event.attempts
        headers = {
            "X-Event-ID": eid,
            "X-Timestamp": str(int(now)),
            "X-Signature": sign(secret, int(now), eid, body),
            "Content-Type": "application/json",
        }
        error = None
        try:
            status = send(body, headers)
            if not 200 <= status < 300:
                error = f"HTTP {status}"
        except (OSError, httpx.HTTPError) as exc:
            error = type(exc).__name__
        state = "delivered" if not error else ("dead" if attempt >= max_attempts else "retry")
        with self.sessions.begin() as s:
            s.execute(
                update(Event)
                .where(Event.id == eid, Event.lease == token)
                .values(state=state, error=error, next_at=now + 2**attempt, lease=None)
            )
        return dict(id=eid, state=state, attempts=attempt, error=error)

    def receive(self, body, headers, secret, now=None):
        now = time.time() if now is None else now
        try:
            ts = int(headers["X-Timestamp"])
            eid = headers["X-Event-ID"]
            expected = sign(secret, ts, eid, body)
            valid = abs(now - ts) <= 300 and hmac.compare_digest(headers["X-Signature"], expected)
        except (ValueError, KeyError):
            valid = False
        if not valid:
            raise PermissionError("invalid or expired signature")
        digest = hashlib.sha256(body).hexdigest()
        # A unique primary key arbitrates simultaneous delivery. Receipt and local
        # business effect share one transaction; an external effect would need its own outbox.
        from sqlalchemy.exc import IntegrityError

        try:
            with self.sessions.begin() as s:
                old = s.get(Receipt, eid)
                if old:
                    if old.payload_hash != digest:
                        raise ValueError("conflicting event body")
                    return {"duplicate": True}
                json.loads(body)
                s.add(Receipt(id=eid, payload_hash=digest, body=body.decode()))
            return {"duplicate": False}
        except IntegrityError:
            with self.sessions() as s:
                if s.get(Receipt, eid).payload_hash != digest:
                    raise ValueError("conflicting event body")
            return {"duplicate": True}

    def status(self):
        with self.sessions() as s:
            return [
                dict(id=e.id, state=e.state, attempts=e.attempts, error=e.error)
                for e in s.scalars(select(Event).order_by(Event.id))
            ]


def demo(mode="fixture"):
    with tempfile.TemporaryDirectory() as d:
        engine = DeliveryEngine("sqlite:///" + str(Path(d) / "events.sqlite"))
        engine.enqueue("invoice-42", {"invoice_id": 42, "status": "approved"})
        first = engine.deliver(lambda b, h: 503, "demo-secret", now=100)

        def receiver(body, headers):
            engine.receive(body, headers, "demo-secret", now=103)
            return 200

        second = engine.deliver(receiver, "demo-secret", now=103)
        return {"outage": first, "recovery": second, "events": engine.status()}


def evaluate(mode="fixture"):
    r = demo(mode)
    return {
        "passed": r["outage"]["state"] == "retry" and r["recovery"]["state"] == "delivered",
        "scenario": r,
    }
