# backend/app/models/upload_models.py
from fastapi import UploadFile
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

# 建物情報（構造、階数、面積、用途、築年数）
class BuildingInfo(BaseModel):
  structure: str = Field(..., description="構造形式（例: RC, S, 木造）")
  floors: int = Field(..., ge=1, description="階数（整数, 最低1）")
  area: float = Field(..., gt=0, description="延床面積 (㎡)（正の数）")
  usage: str = Field(..., description="用途（例: オフィス, 住宅）")
  building_age: int = Field(..., ge=0, description="築年数（年, 0以上）")
# 位置情報（緯度・経度・都道府県コード）
class LocationInfo(BaseModel):
  lat: float = Field(..., description="緯度（例: 35.68）")
  lon: float = Field(..., description="経度（例: 139.76）")
  pref_code: str = Field(..., description="都道府県コード（例: '13'）")
# フロントから送信されるネスト構造リクエスト
class EstimateWithLocationRequest(BaseModel):
  building: BuildingInfo
  location: LocationInfo
# 地価データ情報
class LandPriceInfo(BaseModel):
  location: str = Field(..., description="地価データ上の地点名称")
  price: float = Field(..., description="地価（円/㎡）")
  use: Optional[str] = Field(None, description="地価用途区分")
  year: Optional[int] = Field(None, description="年度")
  distance_m: float = Field(..., description="対象点との距離（メートル）")
# レスポンス（見積金額＋地域＋地価情報）
class EstimateResponse(BaseModel):
  estimated_cost: float = Field(..., description="推定された建設費")
  region: str = Field(..., description="最寄り地価データから得た地域名")
  land_price_info: Optional[LandPriceInfo] = Field(
      None, description="最寄り地価データの詳細（利用可能な場合）"
  )
  history_id: Optional[int] = Field(None, description="履歴保存時のレコードID（オプション）")

# 最新のクラス定義
class UploadDTO(BaseModel):
    file: UploadFile
    metadata: Dict[str, Any]