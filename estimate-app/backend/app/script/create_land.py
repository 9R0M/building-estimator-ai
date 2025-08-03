import os

import geopandas as gpd

import pandas as pd

# --- ディレクトリ設定 ---

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_PATH = os.path.normpath(os.path.join(BASE_DIR, "../../data/land_price/all_landprice.parquet"))

OUTPUT_DIR = os.path.normpath(os.path.join(BASE_DIR, "../../data/land_price/prefectures"))

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- 都道府県マップ ---

pref_map = {

    "北海道": "01", "青森": "02", "岩手": "03", "宮城": "04", "秋田": "05", "山形": "06", "福島": "07",

    "茨城": "08", "栃木": "09", "群馬": "10", "埼玉": "11", "千葉": "12", "東京": "13", "神奈川": "14",

    "新潟": "15", "富山": "16", "石川": "17", "福井": "18", "山梨": "19", "長野": "20", "岐阜": "21",

    "静岡": "22", "愛知": "23", "三重": "24", "滋賀": "25", "京都": "26", "大阪": "27", "兵庫": "28",

    "奈良": "29", "和歌山": "30", "鳥取": "31", "島根": "32", "岡山": "33", "広島": "34", "山口": "35",

    "徳島": "36", "香川": "37", "愛媛": "38", "高知": "39", "福岡": "40", "佐賀": "41", "長崎": "42",

    "熊本": "43", "大分": "44", "宮崎": "45", "鹿児島": "46", "沖縄": "47"

}

# --- 建物用途別 単価（万円/㎡） ---

unit_prices = {

    "ビル": 50,

    "住宅": 25,

    "オフィス": 40,

    "工場": 30,

    "学校": 35,

    "商業施設": 45,

    "病院": 55,

    "倉庫": 20,

    "公共施設": 32,

    "宿泊施設": 38,

    "宗教施設": 26,

    "水道・交通施設": 28,

    "墓地": 15,

    "その他": 22

}

# --- 地価データ読み込み ---

print(f" 読み込み: {INPUT_PATH}")

gdf = gpd.read_parquet(INPUT_PATH)

if "L01_006" not in gdf.columns or "L01_001" not in gdf.columns:

    raise ValueError("必要なカラム L01_006 または L01_001 が存在しません")

# --- 平均価格倍率追加 ---

national_avg = gdf["L01_006"].mean()

gdf["price_ratio"] = gdf["L01_006"] / national_avg

gdf["pref_name"] = gdf["L01_001"].str[:2]

# --- 用途別㎡単価辞書（倍率補正） ---

def calc_sqm_unit_prices(row):

    ratio = row["price_ratio"]

    return {k: int(v * ratio * 10000) for k, v in unit_prices.items()}  # 円単価へ換算

gdf["building_estimates_sqm_price"] = gdf.apply(calc_sqm_unit_prices, axis=1)

# --- 都道府県別に出力 ---

for pref_name, code in pref_map.items():

    subset = gdf[gdf["pref_name"] == pref_name].copy()

    if subset.empty:

        print(f" {pref_name}（{code}）のデータなし")

        continue

    subset.drop(columns=["pref_name"], inplace=True)

    out_path = os.path.join(OUTPUT_DIR, f"{code}_{pref_name}.parquet")

    subset.to_parquet(out_path, engine="pyarrow")

    print(f"✅ {pref_name} → {len(subset):,}件 保存完了: {out_path}")
 