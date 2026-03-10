# Carrier Integration Sandbox

A simplified simulation of a carrier integration system.

## What this project demonstrates

- Canonical shipment event model
- Booking simulation API
- Webhook ingestion
- State machine transitions
- Validation rules (idempotency, ordering, forbidden transitions)

## Why

Built to showcase integration experience in logistics / TMS environments.

## Structure

- docs/ → schemas, BPMN, diagrams
- src/ → API + state machine
- tests/ → validation + flow tests

## Demo flow

Happy path tested in Swagger:

1. BOOKING_CREATED
2. CONTAINER_ASSIGNED
3. GATE_IN
4. LOAD_ON_VESSEL
5. VESSEL_DEPARTED
6. VESSEL_ARRIVED
7. DISCHARGED
8. GATE_OUT
9. INVOICE_SUBMITTED
10. INVOICE_APPROVED

Available query endpoints:

- `GET /shipments/{shipment_id}/state`
- `GET /containers/{container_id}/state`
- `GET /shipments/{shipment_id}/events`
- `GET /containers/{container_id}/events`

Example invalid scenario:

- `GATE_OUT` before `DISCHARGED` returns `INVALID_TRANSITION`