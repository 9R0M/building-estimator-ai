#estimate-app\backend\app\models\land_price_dto.py
from typing import Optional
from pydantic import BaseModel, Field

class LandPriceResponse(BaseModel):
    land_price: Optional[float] = None

class LandPriceRequest(BaseModel):
    pref_code: str = Field(
        ...,  # required
        pattern=r"^\d{2}$",
        description="都道府県コード（2桁）"
    )
    usage: Optional[str] = None
    structure: Optional[str] = None
    area: Optional[float] = None  #これを追加
    #lat: float
    #lon: float    


class LandPriceDTO(BaseModel):
    location: str           # 都道府県名（例：東京都）
    use: str                # 用途（例：住宅、ビル、病院）
    structure: Optional[str] = None       # ← NEW: RC, SRC, Sなど
    price: float            # 用途別価格（地価 × 倍率）
    base_price: Optional[float] = None  # 元の地価目安（オプション）
    factor: Optional[float] = None      # 倍率（オプション）
    year: Optional[int] = None          # 年度（未使用ならNone）
    distance_m: Optional[float] = None  # 未使用（将来GPS用）
    source: Optional[str] = None        # データソース（例：split）
    total_price: Optional[float] = None   # 面積を掛けた合計