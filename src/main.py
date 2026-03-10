from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Carrier Integration Sandbox", version="0.2.0")

# In-memory storage (demo purpose)
EVENTS: Dict[str, "Event"] = {}
STATE_BY_SHIPMENT: Dict[str, str] = {}
STATE_BY_CONTAINER: Dict[str, str] = {}

EventType = Literal[
    "BOOKING_CREATED",
    "CONTAINER_ASSIGNED",
    "GATE_IN",
    "LOAD_ON_VESSEL",
    "VESSEL_DEPARTED",
    "VESSEL_ARRIVED",
    "DISCHARGED",
    "GATE_OUT",
    "INVOICE_SUBMITTED",
    "INVOICE_APPROVED",
]


def next_state_from_event(event_type: str) -> str:
    mapping = {
        "BOOKING_CREATED": "BOOKED",
        "CONTAINER_ASSIGNED": "CONTAINER_ASSIGNED",
        "GATE_IN": "GATED_IN",
        "LOAD_ON_VESSEL": "LOADED_ON_VESSEL",
        "VESSEL_DEPARTED": "DEPARTED",
        "VESSEL_ARRIVED": "ARRIVED",
        "DISCHARGED": "DISCHARGED",
        "GATE_OUT": "GATED_OUT",
        "INVOICE_SUBMITTED": "INVOICED",
        "INVOICE_APPROVED": "CLOSED",
    }
    return mapping.get(event_type, "UNKNOWN")


def allowed_next_event_types(current_state: Optional[str]) -> List[str]:
    if current_state is None:
        return ["BOOKING_CREATED"]
    if current_state == "BOOKED":
        return ["CONTAINER_ASSIGNED"]
    if current_state == "CONTAINER_ASSIGNED":
        return ["GATE_IN"]
    if current_state == "GATED_IN":
        return ["LOAD_ON_VESSEL"]
    if current_state == "LOADED_ON_VESSEL":
        return ["VESSEL_DEPARTED"]
    if current_state == "DEPARTED":
        return ["VESSEL_ARRIVED"]
    if current_state == "ARRIVED":
        return ["DISCHARGED"]
    if current_state == "DISCHARGED":
        return ["GATE_OUT"]
    if current_state == "GATED_OUT":
        return ["INVOICE_SUBMITTED"]
    if current_state == "INVOICED":
        return ["INVOICE_APPROVED"]
    if current_state == "CLOSED":
        return []
    return []


class Event(BaseModel):
    event_id: str = Field(..., description="Unique event id")
    event_type: EventType
    event_time: datetime
    source_system: str
    correlation_id: str
    shipment_id: str
    container_id: Optional[str] = None
    vessel_voyage: Optional[str] = None
    location_unlocode: Optional[str] = None
    payload: dict = Field(default_factory=dict)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/webhook/events")
def ingest_event(event: Event):
    if event.event_id in EVENTS:
        return {
            "status": "duplicate",
            "event_id": event.event_id,
            "shipment_id": event.shipment_id,
            "new_state": STATE_BY_SHIPMENT.get(event.shipment_id),
        }

    current_state = STATE_BY_SHIPMENT.get(event.shipment_id)
    allowed = allowed_next_event_types(current_state)

    if event.event_type not in allowed:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_TRANSITION",
                "shipment_id": event.shipment_id,
                "current_state": current_state,
                "event_type": event.event_type,
                "allowed_event_types": allowed,
            },
        )

    EVENTS[event.event_id] = event
    new_state = next_state_from_event(event.event_type)

    STATE_BY_SHIPMENT[event.shipment_id] = new_state

    if event.container_id:
        STATE_BY_CONTAINER[event.container_id] = new_state

    return {
        "status": "accepted",
        "event_id": event.event_id,
        "shipment_id": event.shipment_id,
        "old_state": current_state,
        "new_state": new_state,
    }


@app.get("/shipments/{shipment_id}/state")
def get_shipment_state(shipment_id: str):
    return {
        "shipment_id": shipment_id,
        "state": STATE_BY_SHIPMENT.get(shipment_id),
    }


@app.get("/containers/{container_id}/state")
def get_container_state(container_id: str):
    return {
        "container_id": container_id,
        "state": STATE_BY_CONTAINER.get(container_id),
    }


@app.get("/shipments/{shipment_id}/events")
def get_shipment_events(shipment_id: str):
    shipment_events = [
        event for event in EVENTS.values() if event.shipment_id == shipment_id
    ]
    shipment_events.sort(key=lambda e: e.event_time)
    return {
        "shipment_id": shipment_id,
        "event_count": len(shipment_events),
        "events": shipment_events,
    }


@app.get("/containers/{container_id}/events")
def get_container_events(container_id: str):
    container_events = [
        event for event in EVENTS.values() if event.container_id == container_id
    ]
    container_events.sort(key=lambda e: e.event_time)
    return {
        "container_id": container_id,
        "event_count": len(container_events),
        "events": container_events,
    }