from logistics.shipment import Shipment


def dispatch_endpoint(shipment: Shipment, driver_id: str, now: str) -> dict:
    # POST /shipments/<id>/dispatch
    if shipment.status != "packed":
        return {"error": "not packed"}
    if shipment.voided_at is not None:
        return {"error": "voided"}
    shipment.status = "dispatched"
    shipment.is_dispatched = True
    shipment.driver_id = driver_id
    shipment.dispatched_at = now
    return {"ok": True}
