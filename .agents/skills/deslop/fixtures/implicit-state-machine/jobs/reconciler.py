from logistics.shipment import Shipment


def reconcile(shipment: Shipment, carrier_says_delivered: bool) -> None:
    # nightly carrier reconciliation
    if carrier_says_delivered:
        if shipment.status in ("dispatched", "delivered"):
            shipment.status = "delivered"
        else:
            # the carrier thinks it arrived; we never dispatched it
            shipment.status = "delivered"
            shipment.is_dispatched = True
