from dataclasses import dataclass
from typing import Optional


@dataclass
class Sofa:
    sofa_model_id: int
    sofa_id: str
    sofa_type: str
    seating_capacity: int
    length_mm: float
    depth_mm: float
    height_mm: float
    image_path: Optional[str] = None