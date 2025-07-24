# backend/app/routers/land_price.py
from fastapi import APIRouter, HTTPException, Query
from geopy.distance import geodesic
import logging
import geopandas as gpd
from app.models.estimate_models import LandPriceDTO
from app.services.logic.land_price_models import (load_land_price_data, load_old_land_price_data
)
router = APIRouter(prefix="/land-price", tags=["land-price"])
logger = logging.getLogger(__name__)
def _safe_cast(value, default, cast_func):
   try:
       return cast_func(value) if value is not None else default
   except (ValueError, TypeError):
       return default
@router.get("/", response_model=LandPriceDTO, summary="最寄り地価を取得（現行＋旧年度対応）")
async def get_land_price(
   lat: float = Query(..., ge=-90, le=90, description="緯度"),
   lon: float = Query(..., ge=-180, le=180, description="経度"),
   pref_code: str = Query(..., regex=r"^\d{2}$", description="都道府県コード（2桁）")
):
   logger.info(f"地価取得リクエスト: lat={lat}, lon={lon}, pref_code={pref_code}")
   # 現行年度読み込み
   try:
       gdf = load_land_price_data(pref_code)
       if gdf.empty:
           raise FileNotFoundError("現行データなし")
       source = "current"
   except FileNotFoundError:
       logger.warning(f"現行年度データなし → 過去年度データ検索へ：pref_code={pref_code}")
       try:
           gdf = load_old_land_price_data(pref_code)
           if gdf.empty:
               raise HTTPException(status_code=404, detail="過去年度含めて地価データなし")
           source = "old"
       except FileNotFoundError:
           logger.error(f"地価データが一切見つかりません: pref_code={pref_code}")
           raise HTTPException(status_code=404, detail="地価データが見つかりません")
       except Exception as e:
           logger.exception(f"過去年度データ読み込みエラー: {e}")
           raise HTTPException(status_code=500, detail="過去年度地価データ読み込み失敗")
   except Exception as e:
       logger.exception(f"現行データ読み込みエラー: {e}")
       raise HTTPException(status_code=500, detail="地価データ読み込み失敗")
   # 距離計算と最寄点検索
   try:
       target = (lat, lon)
       gdf = gdf.to_crs(epsg=4326) if hasattr(gdf, "crs") else gdf
       gdf["distance"] = gdf.geometry.apply(lambda geom: geodesic((geom.y, geom.x), target).meters)
       nearest = gdf.loc[gdf["distance"].idxmin()]
   except Exception as e:
       logger.exception(f"最寄点検索エラー（lat={lat}, lon={lon}）: {e}")
       raise HTTPException(status_code=500, detail="地価データ解析に失敗しました")
   # DTO整形
   return LandPriceDTO(
       location=_safe_cast(nearest.get("L01_001"), "", str),
       price=_safe_cast(nearest.get("L01_006"), 0.0, float),
       use=_safe_cast(nearest.get("L01_003"), "", str),
       year=_safe_cast(nearest.get("L01_002"), None, int),
       distance_m=round(_safe_cast(nearest["distance"], 0.0, float), 1),
       source=source
   )