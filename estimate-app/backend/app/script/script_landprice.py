import geopandas as gpd

import os

# --- 入力元（GeoJSONまたはCSV） ---

INPUT_GEOJSON = r"C:\Users\tkrly\building-estimator-ai\estimate-app\backend\data\land_price\original\landprice.geojson"

# or CSVなら：

# INPUT_CSV = r"C:\Users\tkrly\building-estimator-ai\estimate-app\backend\data\land_price\original\landprice.csv"

# --- 出力先（Parquet） ---

OUTPUT_PARQUET = r"C:\Users\tkrly\building-estimator-ai\estimate-app\backend\data\land_price\all_landprice.parquet"

# --- 読み込み ---

gdf = gpd.read_file(INPUT_GEOJSON)  # CSVなら pd.read_csv()

# --- Parquet 書き出し ---

gdf.to_parquet(OUTPUT_PARQUET, engine="pyarrow")

print(f"✅ Parquet生成完了 → {OUTPUT_PARQUET}（{len(gdf)} 件）")
 