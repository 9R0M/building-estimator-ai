import os
import geopandas as gpd
import pandas as pd
# --- region_factors の定義 ---
region_factors = {
"北海道": 1.05,"青森": 0.95,"岩手": 0.95,"宮城": 1.00,"秋田": 0.94,
"山形": 0.95,"福島": 0.97,"茨城": 1.00, "栃木": 0.99, "群馬": 0.98,
"埼玉": 1.08,"千葉": 1.08,"東京": 1.20,"神奈川": 1.15,"新潟": 0.96,
"富山": 0.97,"石川": 0.98,"福井": 0.96,"山梨": 0.98,"長野": 0.97,
"岐阜": 0.98,"静岡": 1.02,"愛知": 1.10,"三重": 0.98,"滋賀": 0.99,
"京都": 1.05,"大阪": 1.15,"兵庫": 1.08,"奈良": 0.97,"和歌山": 0.96,
"鳥取": 0.94,"島根": 0.94,"岡山": 0.98,"広島": 1.00,"山口": 0.97,
"徳島": 0.95,"香川": 0.96,"愛媛": 0.96,"高知": 0.95,"福岡": 1.05,
"佐賀": 0.94,"長崎": 0.95,"熊本": 0.96,"大分": 0.96,"宮崎": 0.94,
"鹿児島": 0.95,"沖縄": 1.10,"その他": 1.00
}
# --- ファイルパス設定 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "backend", "data", "land_price", "all_landprice.parquet")
OUTPUT_FILE = os.path.join(BASE_DIR, "backend", "data", "land_price", "all_landprice_with_factors.parquet")
# --- 地価データの読み込み ---
print(f"読み込み: {INPUT_FILE}")
gdf = gpd.read_parquet(INPUT_FILE)
print(f"地価データ件数: {len(gdf)}")
# --- 都道府県名の抽出（住所の先頭2文字） ---
gdf["pref_name"] = gdf["L01_001"].str[:2]
# --- region_factors を DataFrame に変換 ---
region_df = pd.DataFrame([
   {"pref_name": k, "region_factor": v}
   for k, v in region_factors.items()
])
# --- 地価データとマージ ---
merged = gdf.merge(region_df, on="pref_name", how="left")
# --- 補正価格列を追加 ---
merged["adjusted_price"] = merged["L01_006"] * merged["region_factor"]
# --- 不正データ除去 ---
merged = merged[merged["adjusted_price"].notnull()]
# --- 保存 ---
merged.to_parquet(OUTPUT_FILE)
print(f"保存完了: {OUTPUT_FILE}")