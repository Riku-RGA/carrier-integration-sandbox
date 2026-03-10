# Container Lifecycle (Event Flow)

This sandbox simulates a simplified container shipment lifecycle typical in ocean freight operations.

The system receives carrier events through a webhook and updates shipment and container state accordingly.

## Happy Path Event Sequence

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

## State Progression

Shipment / container state progresses through the following stages:
