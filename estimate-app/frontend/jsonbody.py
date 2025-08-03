# app/models/land_price_dto.py
from pydantic import BaseModel, Field
from typing import Optional

class LandPriceRequest(BaseModel):
    pref_code: str = Field(
        ...,
        pattern=r"^\d{2}$",
        description="都道府県コード（2桁）"
    )

class LandPriceDTO(BaseModel):
    land_price: Optional[float] = None
    source: Optional[str] = None
