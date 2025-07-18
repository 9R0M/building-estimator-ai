# backend/app/routers/land_price.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import logging
from app.services.land_price_models import (
   load_land_price_data,
   load_old_land_price_data,
   find_nearest_land_price,
)
router = APIRouter(prefix="/land-price", tags=["land-price"])
logger = logging.getLogger(__name__)
class LandPriceResponse(BaseModel):
   location: str
   price: float
   use: Optional[str]
   year: Optional[int]
   distance_m: float
   source: str  # "current" または "old"
@router.get(
   "/",
   response_model=LandPriceResponse,
   summary="最寄り地価を取得",
   description="緯度・経度・都道府県コードから最寄りの地価を返します。現行データがなければ過去データを参照します。"
)
async def get_land_price(
   lat: float = Query(..., ge=-90.0, le=90.0, description="緯度（-90〜90）"),
   lon: float = Query(..., ge=-180.0, le=180.0, description="経度（-180〜180）"),
   pref_code: str = Query(..., regex=r"^\d{2}$", description="都道府県コード（2桁）"),
):
   logger.info(f"地価取得リクエスト: lat={lat}, lon={lon}, pref={pref_code}")
   # Step 1: データ読込 current → old フォールバック
   source = "current"
   try:
       gdf = load_land_price_data(pref_code)
       if gdf.empty:
           raise FileNotFoundError("現行地価データが空です")
   except FileNotFoundError:
       logger.warning("現行データなし → OLD にフォールバック")
       try:
           gdf = load_old_land_price_data(pref_code)
           source = "old"
           if gdf.empty:
               raise HTTPException(status_code=404, detail="地価データが見つかりません")
       except FileNotFoundError:
           logger.error("地価データ一切なし")
           raise HTTPException(status_code=404, detail="地価データが見つかりません")
       except Exception as e:
           logger.exception("OLDデータ読み込みエラー")
           raise HTTPException(status_code=500, detail=f"地価の読み込みに失敗しました: {e}")
   except Exception as e:
       logger.exception("現行データ読み込みエラー")
       raise HTTPException(status_code=500, detail=f"地価の読み込みに失敗しました: {e}")
   # Step 2: 距離計算で最近傍レコード取得
   try:
       nearest = find_nearest_land_price(gdf, lat, lon)
   except Exception as e:
       logger.exception("距離計算エラー")
       raise HTTPException(status_code=500, detail=f"最寄地価取得失敗: {e}")
   # Step 3: 年度パース（数値変換）
   year: Optional[int] = None
   try:
       val = nearest.get("L01_002")
       if val is not None:
           year = int(val)
   except Exception:
       logger.warning(f"年度パース失敗: {nearest.get('L01_002')}")
   return LandPriceResponse(
       location=nearest.get("L01_001", ""),
       price=float(nearest.get("L01_006", 0)),
       use=nearest.get("L01_003"),
       year=year,
       distance_m=round(nearest.distance, 1),
       source=source,
   )