from dataclasses import dataclass
from typing import Optional


@dataclass
class Material:
    material_id: int
    material_name: str
    material_category: Optional[str]
    unit: str
    description: Optional[str] = None
    unit_price_inr: Optional[float] = None