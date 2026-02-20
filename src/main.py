from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional

app = FastAPI(title="Carrier Integration Sandbox", version="0.1.0")

class Event(BaseModel):
    event_id: str
    event_type: str
    event_time: str
    source_system: str
    correlation_id: str
    shipment_id: str
    container_id: Optional[str] = None
    vessel_voyage: Optional[str] = None
    location_unlocode: Optional[str] = None
    payload: Dict[str, Any] = {}

# naive in-memory store for now
EVENTS: Dict[str, Event] = {}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/webhook/events")
def ingest_event(event: Event):
    # idempotency
    if event.event_id in EVENTS:
        return {"status": "duplicate", "event_id": event.event_id}

    EVENTS[event.event_id] = event
    return {"status": "accepted", "event_id": event.event_id}