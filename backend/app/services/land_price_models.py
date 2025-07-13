#backend/app/services/land_price_models.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import logging
from geopy.distance import geodesic
from app.services.land_price_models import (
   load_land_price_data,
   load_old_land_price_data,
)
router = APIRouter(prefix="/land-price", tags=["land-price"])
logger = logging.getLogger(__name__)
class LandPriceResponse(BaseModel):
   location: str
   price: float
   use: Optional[str]
   year: Optional[int]
   distance_m: float
   source: str  # "current" or "old"
@router.get("/", response_model=LandPriceResponse, summary="Get nearest land price")
async def get_land_price(
   lat: float = Query(..., ge=-90, le=90, description="緯度（-90〜90）"),
   lon: float = Query(..., ge=-180, le=180, description="経度（-180〜180）"),
   pref_code: str = Query(..., regex=r"^\d{2}$", description="都道府県コード（2桁）")
):
   logger.info(f"地価取得リクエスト: lat={lat}, lon={lon}, pref_code={pref_code}")
   # --- Step1: 現行年度 or 過去年度データ
   try:
       gdf = load_land_price_data(pref_code)
       if gdf.empty:
           raise HTTPException(status_code=404, detail="現行年度の地価データが存在しません")
       source = "current"
   except FileNotFoundError:
       logger.warning("現行年度データなし → 過去年度に切替")
       try:
           gdf = load_old_land_price_data(pref_code)
           if gdf.empty:
               raise HTTPException(status_code=404, detail="過去年度含め地価データが見つかりません")
           source = "old"
       except FileNotFoundError:
           logger.error("地価データが一切存在しません")
           raise HTTPException(status_code=404, detail="地価データが見つかりません")
       except HTTPException:
           raise
       except Exception:
           logger.exception("過去年度地価データ読み込み中にエラー")
           raise HTTPException(status_code=500, detail="過去年度データ読み込み失敗")
   except HTTPException:
       raise
   except Exception:
       logger.exception("現行年度地価データ読み込み中にエラー")
       raise HTTPException(status_code=500, detail="地価データ読み込みに失敗しました")
   # --- Step2: 最近傍点算出
   try:
       df = gdf.assign(
           distance=gdf.geometry.apply(lambda geom: geodesic((geom.y, geom.x), (lat, lon)).meters)
       )
       nearest = df.loc[df.distance.idxmin()]
   except Exception:
       logger.exception("最近傍点算出中にエラー")
       raise HTTPException(status_code=500, detail="地価データ解析に失敗しました")
   # --- Step3: レスポンス整形
   year_val = nearest.get("L01_002")
   try:
       year = int(year_val) if year_val is not None else None
   except Exception:
       logger.warning(f"年度変換失敗: {year_val}")
       year = None
   return LandPriceResponse(
       location=nearest.get("L01_001", ""),
       price=float(nearest.get("L01_006", 0)),
       use=nearest.get("L01_003"),
       year=year,
       distance_m=round(nearest.distance, 1),
       source=source,
   )
   lat: float = Query(..., ge=-90, le=90, description="緯度（-90〜90）"),
   lon: float = Query(..., ge=-180, le=180, description="経度（-180〜180）"),
   pref_code: str = Query(..., regex=r"^\d{2}$", description="都道府県コード（2桁）")
):
   logger.info(f"地価取得リクエスト: lat={lat}, lon={lon}, pref_code={pref_code}")
   # --- Step1: 現行年度 or 過去年度データ
   try:
       gdf = load_land_price_data(pref_code)
       if gdf.empty:
           raise HTTPException(status_code=404, detail="現行年度の地価データが存在しません")
       source = "current"
   except FileNotFoundError:
       logger.warning("現行年度データなし → 過去年度に切替")
       try:
           gdf = load_old_land_price_data(pref_code)
           if gdf.empty:
               raise HTTPException(status_code=404, detail="過去年度含め地価データが見つかりません")
           source = "old"
       except FileNotFoundError:
           logger.error("地価データが一切存在しません")
           raise HTTPException(status_code=404, detail="地価データが見つかりません")
       except HTTPException:
           raise
       except Exception:
           logger.exception("過去年度地価データ読み込み中にエラー")
           raise HTTPException(status_code=500, detail="過去年度データ読み込み失敗")
   except HTTPException:
       raise
   except Exception:
       logger.exception("現行年度地価データ読み込み中にエラー")
       raise HTTPException(status_code=500, detail="地価データ読み込みに失敗しました")
   # --- Step2: 最近傍点算出
   try:
       df = gdf.assign(
           distance=gdf.geometry.apply(lambda geom: geodesic((geom.y, geom.x), (lat, lon)).meters)
       )
       nearest = df.loc[df.distance.idxmin()]
   except Exception:
       logger.exception("最近傍点算出中にエラー")
       raise HTTPException(status_code=500, detail="地価データ解析に失敗しました")
   # --- Step3: レスポンス整形
   year_val = nearest.get("L01_002")
   try:
       year = int(year_val) if year_val is not None else None
   except Exception:
       logger.warning(f"年度変換失敗: {year_val}")
       year = None
   return LandPriceResponse(
       location=nearest.get("L01_001", ""),
       price=float(nearest.get("L01_006", 0)),
       use=nearest.get("L01_003"),
       year=year,
       distance_m=round(nearest.distance, 1),
       source=source,
   )