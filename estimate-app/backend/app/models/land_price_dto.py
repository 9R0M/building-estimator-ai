#estimate-app\backend\app\models\land_price_dto.py
from typing import Optional
from pydantic import BaseModel


class LandPriceDTO(BaseModel):
    location: str
    price: float
    use: Optional[str] = None
    year: Optional[int] = None
    distance_m: float
    source: str = "current" # "current" or "old"