from functools import lru_cache
import geopandas as gpd
import os
@lru_cache()
def load_land_price_data(pref_code: str) -> gpd.GeoDataFrame:
   """
   地価データを都道府県コードで読み込む（GeoDataFrameで返す）
   """
   file_path = os.path.join("data", f"{pref_code}.geojson")  # または .gml
   if not os.path.exists(file_path):
       raise FileNotFoundError(f"ファイルが存在しません: {file_path}")
   return gpd.read_file(file_path)