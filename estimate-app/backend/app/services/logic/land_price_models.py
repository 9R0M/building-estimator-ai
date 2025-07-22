from fastapi import APIRouter, HTTPException, Query
from geopy.distance import geodesic
import logging
from app.models.estimate_models import LandPriceDTO
from app.services.logic.land_price_models import load_land_price_data, load_old_land_price_data
router = APIRouter(prefix="/land-price", tags=["land-price"])
logger = logging.getLogger(__name__)
def _safe_cast(value, default, cast):
   try:
       return cast(value) if value is not None else default
   except (ValueError, TypeError):
       return default
@router.get("/", response_model=LandPriceDTO, summary="最寄り地価取得（現行＋旧年度対応）")
async def get_land_price(
   lat: float = Query(..., description="緯度（例: 35.66）"),
   lon: float = Query(..., description="経度（例: 139.70）"),
   pref_code: str = Query(..., regex=r"^\d{2}$", description="都道府県コード（2桁）")
):
   logger.info(f"地価取得 req: lat={lat}, lon={lon}, pref={pref_code}")
   source = "current"
   # --- ① 現行データ読み込み ---
   try:
       gdf = load_land_price_data(pref_code) #FIX
       if gdf.empty:
           raise FileNotFoundError("現行データなし")
   except FileNotFoundError:
       logger.warning("現行データなし → 過去年度データへフォールバック")
       try:
           gdf = load_old_land_price_data(pref_code) #FIX
           if gdf.empty:
               raise FileNotFoundError("旧年度データなし")
           source = "old"
       except FileNotFoundError:
           logger.error("地価データが一切見つかりません")
           raise HTTPException(status_code=404, detail="地価データが見つかりません")
       except Exception as e:
           logger.exception(f"旧年度データ読み込みエラー: {e}")
           raise HTTPException(status_code=500, detail="旧データ読込失敗")
   except Exception as e:
       logger.exception(f"現行データ読込エラー: {e}")
       raise HTTPException(status_code=500, detail="地価データ読込失敗")
   # --- ② 最寄点検索 ---
   try:
       if hasattr(gdf, "crs") and gdf.crs:
           gdf = gdf.to_crs(epsg=4326)
       target = (lat, lon)
       gdf["distance"] = gdf.geometry.apply(
           lambda geom: geodesic((geom.y, geom.x), target).meters
       )
       nearest = gdf.loc[gdf["distance"].idxmin()]
   except Exception as e:
       logger.exception(f"最寄地価算出エラー: {e}")
       raise HTTPException(status_code=500, detail="地価データ解析に失敗しました")
   # --- ③ DTO整形と返却 ---
   return LandPriceDTO(
       location=_safe_cast(nearest.get("L01_001"), "", str),
       price=_safe_cast(nearest.get("L01_006"), 0.0, float),
       use=_safe_cast(nearest.get("L01_003"), "", str),
       year=_safe_cast(nearest.get("L01_002"), None, int),
       distance_m=round(_safe_cast(nearest["distance"], 0.0, float), 1),
       source=source
   )