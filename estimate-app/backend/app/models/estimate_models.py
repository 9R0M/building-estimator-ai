#estimate-app\backend\app\models\estimate_models.py
from typing import Dict, Optional
from pydantic import BaseModel
from .land_price_dto import LandPriceDTO


class EstimateRequest(BaseModel):
    structure: str
    area: float
    floors: int
    usage: str
    building_age: int
    lat: float
    lon: float
    pref_code: str


class EstimateResponse(BaseModel):
    estimated_amount: float
    breakdown: Dict[str, float]
    land_price: Optional[LandPriceDTO] = None
    # app/models/estimate_models.py
