
# # backend/app/services/land_price_models.py

# import os
# import logging
# import geopandas as gpd
# from fastapi import HTTPException
# from geopy.distance import geodesic
# from app.models import LandPriceResponse # TODO:仮置きなので今後修正必要

# logger = logging.getLogger(__name__)

# # 定数定義（キー・拡張子）
# KEY_LOCATION = "L01_001"
# KEY_USE      = "L01_003"
# KEY_YEAR     = "L01_002"
# KEY_PRICE    = "L01_006"
# SUPPORTED_EXT = (".parquet", ".geojson")

# # データフォルダ設定
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DATA_DIR = os.path.normpath(os.path.join(BASE_DIR, "../../data/land_price"))

# def load_geo_dataframe(path: str) -> gpd.GeoDataFrame:
#     if not os.path.exists(path):
#         logger.debug(f"ファイル未検出: {path}")
#         raise FileNotFoundError(path)
#     try:
#         # GeoPandas のバージョン依存対応
#         if hasattr(gpd, "__version__") and gpd.__version__ >= "0.14":
#             gdf = gpd.read_file(path, use_arrow=True)
#         else:
#             gdf = gpd.read_file(path)
#         logger.info(f"GeoDataFrame 読込成功: {os.path.basename(path)}（{len(gdf)}件）")
#         return gdf
#     except Exception:
#         logger.exception(f"GeoDataFrame 読込エラー: {path}")
#         raise

# def _scan_files(pref_code: str, suffix: str) -> gpd.GeoDataFrame:
#     for ext in SUPPORTED_EXT:
#         path = os.path.join(DATA_DIR, f"{pref_code}_{suffix}{ext}")
#         try:
#             return load_geo_dataframe(path)
#         except FileNotFoundError:
#             continue
#     raise FileNotFoundError(f"{suffix}データ未検出: {pref_code}_{suffix}")

# def load_land_price_data(pref_code: str) -> gpd.GeoDataFrame:
#     """現行年度データ."""
#     return _scan_files(pref_code, "current")

# def load_old_land_price_data(pref_code: str) -> gpd.GeoDataFrame:
#     """過去年度データ."""
#     return _scan_files(pref_code, "old")

# def get_nearest_land_price(lat: float, lon: float, pref_code: str) -> LandPriceResponse:
#     """最寄地価情報を取得してPydantic型で返す。"""
#     # データ取得（現行＞過去）
#     try:
#         gdf = load_land_price_data(pref_code)
#         source = "current"
#     except FileNotFoundError:
#         logger.warning(f"現行データなし → 過去年度検索 pref={pref_code}")
#         try:
#             gdf = load_old_land_price_data(pref_code)
#             source = "old"
#         except FileNotFoundError:
#             logger.error(f"地価データ未発見 pref={pref_code}")
#             raise HTTPException(status_code=404, detail="地価データが見つかりません")

#     if gdf.empty:
#         logger.warning("取得データが空")
#         raise HTTPException(status_code=404, detail="地価データが空です")

#     # 最近傍レコードを距離計算で検索
#     try:
#         df = gdf.copy()
#         df["distance"] = df.geometry.apply(
#             lambda geom: geodesic((geom.y, geom.x), (lat, lon)).meters
#         )
#         nearest = df.loc[df["distance"].idxmin()]
#     except Exception:
#         logger.exception("最近傍検索に失敗")
#         raise HTTPException(status_code=500, detail="地価データ解析に失敗しました")

#     # 年度を整数に変換
#     raw_year = nearest.get(KEY_YEAR)
#     try:
#         year = int(raw_year) if raw_year is not None else None
#     except (TypeError, ValueError):
#         logger.warning(f"年度パース失敗: {raw_year}")
#         year = None

#     return LandPriceResponse(
#         location=nearest.get(KEY_LOCATION, ""),
#         price=float(nearest.get(KEY_PRICE, 0)),
#         use=nearest.get(KEY_USE),
#         year=year,
#         distance_m=round(nearest.distance, 1),
#         source=source,
#     )