from pydantic import BaseModel
from typing import List


class QuotationItemResponse(BaseModel):
    component_id: int
    material_id: int
    quantity: float
    unit: str
    unit_price_inr: float
    total_inr: float


class QuotationResponse(BaseModel):
    quotation_id: int | None
    quotation_number: str
    sofa_model_id: int

    material_cost_inr: float
    labour_cost_inr: float
    stitching_cost_inr: float
    overhead_inr: float
    transportation_cost_inr: float
    profit_inr: float
    total_inr: float

    items: List[QuotationItemResponse]