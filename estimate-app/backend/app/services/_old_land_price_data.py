# backend/app/services/land_price_models.py
import geopandas as gpd
import os
import json
import logging
from typing import Dict, Any
from geopy.distance import geodesic
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../data/land_price")
def load_geo_dataframe(path: str) -> gpd.GeoDataFrame:
   if not os.path.exists(path):
       logger.debug(f"[load] 不存在ファイル: {path}")
       raise FileNotFoundError(path)
   ext = os.path.splitext(path)[1].lower()
   try:
       if ext in (".parquet", ".feather"):
           gdf = gpd.read_parquet(path)
       else:
           # use_arrow=True を指定すると高速  [oai_citation_attribution:0‡Medium](https://medium.com/%40v0220225/backend-logging-in-python-and-applied-to-fastapi-7b47118d1d92?utm_source=chatgpt.com) [oai_citation_attribution:1‡GeoPandas](https://geopandas.org/en/stable/docs/user_guide/io.html?utm_source=chatgpt.com)
           gdf = gpd.read_file(path, use_arrow=True)
       logger.info(f"[load] {os.path.basename(path)} 読込成功 ({len(gdf)}件)")
       return gdf
   except Exception:
       logger.exception(f"[load] GeoDataFrame 読込エラー: {path}")
       raise
def load_land_price_data(pref_code: str) -> gpd.GeoDataFrame:
   # 現行データ（parquet優先）()
   for ext in (".parquet", ".geojson"):
       path = os.path.join(DATA_DIR, f"{pref_code}_current{ext}")
       try:
           return load_geo_dataframe(path)
       except FileNotFoundError:
           continue
   raise FileNotFoundError(f"現行地価データ未検出: {pref_code}_current.[parquet|geojson]")
def load_old_land_price_data(pref_code: str) -> gpd.GeoDataFrame:
   # 過去データ対応、parquet優先、学習AI用に長期履歴を蓄積
   for ext in (".parquet", ".geojson"):
       path = os.path.join(DATA_DIR, f"{pref_code}_old{ext}")
       try:
           return load_geo_dataframe(path)
       except FileNotFoundError:
           continue
   raise FileNotFoundError(f"過去地価データ未検出: {pref_code}_old.[parquet|geojson]")
def find_nearest_land_price(
   gdf: gpd.GeoDataFrame,
   lat: float,
   lon: float
) -> Dict[str, Any]:
   if gdf.empty:
       logger.error("[find_nearest] GeoDataFrame が空です")
       raise ValueError("地価データが空です")
   target = (lat, lon)
   try:
       df = gdf.copy()
       df['distance'] = df.geometry.apply(
           lambda geom: geodesic((geom.y, geom.x), target).meters
       )
   except Exception:
       logger.exception("[find_nearest] 距離計算エラー")
       raise RuntimeError("距離計算に失敗しました")
   nearest = df.loc[df['distance'].idxmin()]
   logger.info(f"[find_nearest] 最近傍: 距離={nearest.distance:.1f}m, 緯度経度={lat:.5f},{lon:.5f}")
   year = _safe_int(nearest.get("L01_002"))
   price = _safe_float(nearest.get("L01_006"))
   use = nearest.get("L01_003")
   rec = nearest.drop(labels=['geometry']).to_dict()
   full_json = json.dumps(rec, default=str, ensure_ascii=False)
   return {
       'record': nearest,
       'distance': nearest.distance,
       'year': year,
       'price': price,
       'use': use,
       'full_record_json': full_json,
   }
def _safe_int(val: Any) -> Any:
   try:
       return int(val) if val is not None else None
   except Exception:
       logger.warning(f"[_safe_int] 整数変換失敗: {val}")
       return None
def _safe_float(val: Any) -> Any:
   try:
       return float(val)
   except Exception:
       logger.warning(f"[_safe_float] 浮動小数点変換失敗: {val}")
       return None