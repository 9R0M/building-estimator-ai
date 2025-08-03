import os
import geopandas as gpd
# --- 入力ファイルパス（Parquet データ）---
INPUT_PATH = r"C:\Users\tkrly\building-estimator-ai\estimate-app\backend\app\script\all_landprice.parquet"
# --- 出力先ディレクトリ ---
OUTPUT_DIR = r"C:\Users\tkrly\building-estimator-ai\estimate-app\backend\app\data\land_price\split"
os.makedirs(OUTPUT_DIR, exist_ok=True)
# --- 都道府県名 → コードマップ（01〜47） ---
pref_map = {
   "北海道": "01", "青森": "02", "岩手": "03", "宮城": "04", "秋田": "05", "山形": "06", "福島": "07",
   "茨城": "08", "栃木": "09", "群馬": "10", "埼玉": "11", "千葉": "12", "東京": "13", "神奈川": "14",
   "新潟": "15", "富山": "16", "石川": "17", "福井": "18", "山梨": "19", "長野": "20", "岐阜": "21",
   "静岡": "22", "愛知": "23", "三重": "24", "滋賀": "25", "京都": "26", "大阪": "27", "兵庫": "28",
   "奈良": "29", "和歌山": "30", "鳥取": "31", "島根": "32", "岡山": "33", "広島": "34", "山口": "35",
   "徳島": "36", "香川": "37", "愛媛": "38", "高知": "39", "福岡": "40", "佐賀": "41", "長崎": "42",
   "熊本": "43", "大分": "44", "宮崎": "45", "鹿児島": "46", "沖縄": "47"
}
# --- 読み込み ---
print(f"読み込み: {INPUT_PATH}")
gdf = gpd.read_parquet(INPUT_PATH)
# --- 住所の先頭2文字で都道府県名推定 ---
gdf["pref_name"] = gdf["L01_001"].str[:2]
# --- 各都道府県ごとに出力 ---
for pref_name, code in pref_map.items():
   subset = gdf[gdf["pref_name"] == pref_name]
   if subset.empty:
       print(f"⚠ {pref_name} のデータが見つかりません")
       continue
   out_path = os.path.join(OUTPUT_DIR, f"landprice_{code}.parquet")
   subset.to_parquet(out_path, index=False)
   print(f"✅ 保存完了: {out_path}（{len(subset)} 件）")