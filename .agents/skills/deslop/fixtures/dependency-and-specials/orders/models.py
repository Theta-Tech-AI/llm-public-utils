from dataclasses import dataclass, field


@dataclass
class Order:
    id: str
    tenant: str
    provider: str
    status: str = "new"
    audit_note: str = field(default="")
