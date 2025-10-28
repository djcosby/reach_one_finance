# remittances/normalize.py
from dataclasses import dataclass, asdict
import json
from decimal import Decimal

@dataclass
class ClaimLineNorm:
    payer: str
    check_date: str
    check_amount: str
    client_name: str
    hcpcs_cpt: str
    units: str
    billed_amount: str | None
    paid_amount: str
    service_date: str
    notes: dict

    def asdict(self): return asdict(self)

# Helper functions to handle JSON encoding/decoding
# of Decimal and Date objects
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

def to_json(obj):
    return json.dumps(obj, cls=CustomEncoder, default=str)

def from_json(j):
    return json.loads(j)