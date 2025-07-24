from fastapi import APIRouter, HTTPException, Query
from geopy.distance import geodesic
import logging
import os
import geopandas as gpd
from app.models.estimate_models import LandPriceDTO

router = APIRouter(prefix="/land-price", tags=["land-price"])
logger = logging.getLogger(__name__)
# ---------- データパス設定 ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(BASE_DIR, "../../../data/land_price"))
# ---------- 地価データ読込関数（直接定義） ----------
def load_land_price_data(pref_code: str) -> gpd.GeoDataFrame:
   filename = f"{pref_code}_landprice.parquet"
   path = os.path.join(DATA_DIR, filename)
   if not os.path.exists(path):
       logger.warning(f"地価ファイルが見つかりません: {path}")
       raise FileNotFoundError(path)
   return gpd.read_parquet(path)
def load_old_land_price_data(pref_code: str) -> gpd.GeoDataFrame:
   filename = f"{pref_code}_landprice_old.geojson"
   path = os.path.join(DATA_DIR, filename)
   if not os.path.exists(path):
       logger.warning(f"旧地価ファイルが見つかりません: {path}")
       raise FileNotFoundError(path)
   return gpd.read_file(path)
# ---------- 安全キャスト ----------
def _safe_cast(value, default, cast):
   try:
       return cast(value) if value is not None else default
   except (ValueError, TypeError):
       return default
# ---------- エンドポイント ----------
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
       gdf = load_land_price_data(pref_code)
       if gdf.empty:
           raise FileNotFoundError("現行データなし")
   except FileNotFoundError:
       logger.warning("現行データなし → 過去年度データへフォールバック")
       try:
           gdf = load_old_land_price_data(pref_code)
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