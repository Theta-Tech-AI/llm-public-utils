from logistics.shipment import Shipment


def void_shipment(shipment: Shipment, now: str) -> None:
    """Admin tool: void any shipment."""
    shipment.status = "voided"
    shipment.voided_at = now
    shipment.is_picking = False
