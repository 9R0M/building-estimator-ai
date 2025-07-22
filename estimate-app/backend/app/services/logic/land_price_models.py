# backend/app/services/logic/land_price_models.py
import os
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import geopandas as gpd
import pandas as pd
import logging
from functools import lru_cache
from shapely.geometry import Point
from geopy.distance import geodesic
router = APIRouter(
   prefix="/land-price",
   tags=["land-price"]
)
logger = logging.getLogger(__name__)
class LandPriceResponse(BaseModel):
   location: str
   price: float
   use: Optional[str]
   year: Optional[int]
   distance_m: float
@router.get("/", response_model=LandPriceResponse, summary="Get nearest land price data")
async def get_land_price(
   lat: float = Query(..., description="Latitude, e.g. 35.66"),
   lon: float = Query(..., description="Longitude, e.g. 139.70"),
   pref_code: str = Query(..., description="Prefecture code, e.g. '13'")
):

   """
   指定された緯度・経度・都道府県コードから、
   最寄りの地価データを返します。
   """
   try:
       gdf = load_land_price_data(pref_code)
   except FileNotFoundError as e:
       logger.warning(f"No data for pref_code={pref_code}: {e}")
       raise HTTPException(status_code=404, detail=str(e))
   target = (lat, lon)
   gdf2 = gdf.assign(
       distance=gdf.geometry.apply(lambda geom: geodesic((geom.y, geom.x), target).meters)
   )
   nearest = gdf2.loc[gdf2["distance"].idxmin()]
   def _safe_get_value(series_or_value, default):
       """SeriesまたはスカラーValue から安全に値を取得"""
       if isinstance(series_or_value, pd.Series):
           return series_or_value.iloc[0] if len(series_or_value) > 0 else default
       return series_or_value if series_or_value is not None else default
   
   return LandPriceResponse(
       location=str(_safe_get_value(nearest.get("location"), "")),
       price=float(_safe_get_value(nearest.get("price"), 0)),
       use=str(_safe_get_value(nearest.get("use"), "住宅地")),
       year=int(_safe_get_value(nearest.get("year"), 2024)),
       distance_m=round(float(_safe_get_value(nearest.get("distance"), 0)), 1)
   )

def load_land_price_data(pref_code: str) -> gpd.GeoDataFrame:
    df = pd.DataFrame({        "location": ["デモ地点"],
        "price": [300000],
        "use": ["住宅地"], 
        "year": [2024],
        "geometry": [Point(139.7300, 35.6100)]
        })

    return gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")


# TODO: 以下backend/app/services/_land_price_models.pyからのコピー　確認、修正する
logger = logging.getLogger(__name__)

# 定数定義（キー・拡張子）
KEY_LOCATION = "L01_001"
KEY_USE      = "L01_003"
KEY_YEAR     = "L01_002"
KEY_PRICE    = "L01_006"
SUPPORTED_EXT = (".parquet", ".geojson")

# データフォルダ設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(BASE_DIR, "../../data/land_price"))

def load_geo_dataframe(path: str) -> gpd.GeoDataFrame:
    if not os.path.exists(path):
        logger.debug(f"ファイル未検出: {path}")
        raise FileNotFoundError(path)
    try:
        # GeoPandas のバージョン依存対応
        if hasattr(gpd, "__version__") and gpd.__version__ >= "0.14":
            gdf = gpd.read_file(path, use_arrow=True)
        else:
            gdf = gpd.read_file(path)
        logger.info(f"GeoDataFrame 読込成功: {os.path.basename(path)}（{len(gdf)}件）")
        return gdf
    except Exception:
        logger.exception(f"GeoDataFrame 読込エラー: {path}")
        raise

def _scan_files(pref_code: str, suffix: str) -> gpd.GeoDataFrame:
    for ext in SUPPORTED_EXT:
        path = os.path.join(DATA_DIR, f"{pref_code}_{suffix}{ext}")
        try:
            return load_geo_dataframe(path)
        except FileNotFoundError:
            continue
    raise FileNotFoundError(f"{suffix}データ未検出: {pref_code}_{suffix}")
def load_old_land_price_data(pref_code: str) -> gpd.GeoDataFrame:
    """過去年度データ."""
    return _scan_files(pref_code, "old")