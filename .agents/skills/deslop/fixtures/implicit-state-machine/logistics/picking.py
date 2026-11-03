from logistics.shipment import Shipment


def start_picking(shipment: Shipment) -> None:
    if shipment.status not in ("queued", "picking"):
        raise ValueError("cannot pick a shipment in %s" % shipment.status)
    shipment.status = "picking"
    shipment.is_picking = True


def finish_picking(shipment: Shipment) -> None:
    if not shipment.is_picking:
        raise ValueError("not picking")
    shipment.is_picking = False
    shipment.status = "packed"
