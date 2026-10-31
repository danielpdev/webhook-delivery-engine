from functools import lru_cache
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.core import DeliveryEngine
import os
import httpx
from fastapi import Request

app = FastAPI(title="webhook-delivery-engine")


@lru_cache
def service():
    return DeliveryEngine()


def guarded(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except PermissionError as e:
        raise HTTPException(403, str(e)) from e
    except ValueError as e:
        raise HTTPException(409, str(e)) from e


class EventInput(BaseModel):
    id: str
    payload: dict


@app.post("/api/events")
def enqueue(b: EventInput):
    return {"id": guarded(service().enqueue, b.id, b.payload)}


@app.get("/api/events")
def status():
    return service().status()


@app.post("/api/deliver")
def deliver():
    # Destination is configured by the operator, never accepted from an event body.
    destination = os.getenv("WEBHOOK_DESTINATION", "http://127.0.0.1:8111/api/receive")
    secret = os.getenv("WEBHOOK_SECRET", "local-demo-secret")

    def send(body, headers):
        with httpx.Client(timeout=10) as client:
            return client.post(destination, content=body, headers=headers).status_code

    return service().deliver(send, secret)


@app.post("/api/receive")
async def receive(request: Request):
    body = await request.body()
    headers = {k: request.headers.get(k, "") for k in ["X-Event-ID", "X-Timestamp", "X-Signature"]}
    return guarded(service().receive, body, headers, os.getenv("WEBHOOK_SECRET", "local-demo-secret"))
