# backend/app/routers/land_price.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import geopandas as gpd
import logging
from app.models.estimate_models import LandPriceDTO
from app.models.land_price_dto import LandPriceRequest

# ---------- ルーター設定 ----------
router = APIRouter(prefix="/api/land-price", tags=["land-price"])

# ---------- ログ設定 ----------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ---------- 都道府県コード → 名称マッピング ----------
PREF_CODE_TO_NAME = {
    "01": "北海道", "02": "青森県", "03": "岩手県", "04": "宮城県", "05": "秋田県",
    "06": "山形県", "07": "福島県", "08": "茨城県", "09": "栃木県", "10": "群馬県",
    "11": "埼玉県", "12": "千葉県", "13": "東京都", "14": "神奈川県", "15": "新潟県",
    "16": "富山県", "17": "石川県", "18": "福井県", "19": "山梨県", "20": "長野県",
    "21": "岐阜県", "22": "静岡県", "23": "愛知県", "24": "三重県", "25": "滋賀県",
    "26": "京都府", "27": "大阪府", "28": "兵庫県", "29": "奈良県", "30": "和歌山県",
    "31": "鳥取県", "32": "島根県", "33": "岡山県", "34": "広島県", "35": "山口県",
    "36": "徳島県", "37": "香川県", "38": "愛媛県", "39": "高知県",
    "40": "福岡県", "41": "佐賀県", "42": "長崎県", "43": "熊本県", "44": "大分県",
    "45": "宮崎県", "46": "鹿児島県", "47": "沖縄県",
}

# ---------- splitディレクトリへの絶対パス ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPLIT_DIR = os.path.normpath(os.path.join(BASE_DIR, "app/script/data/land_price/split"))

# ---------- 安全な型変換 ----------
def _safe_cast(value, default, cast_func):
    try:
        return cast_func(value) if value is not None else default
    except (ValueError, TypeError):
        return default

# ---------- splitファイルの読み込み ----------
def load_split_land_price(pref_name: str) -> gpd.GeoDataFrame:
    path = os.path.join(SPLIT_DIR, f"{pref_name}.parquet")
    if not os.path.exists(path):
        logger.warning(f"地価ファイルが見つかりません: {path}")
        raise FileNotFoundError(f"地価ファイルが見つかりません: {path}")
    return gpd.read_parquet(path)

# ---------- 地価取得エンドポイント（POST） ----------
@router.post("/", response_model=LandPriceDTO, summary="地価取得（split形式）")
async def get_land_price(req: LandPriceRequest):
    logger.info(f"地価取得リクエスト: {req}")

    pref_code = req.pref_code
    pref_name = PREF_CODE_TO_NAME.get(pref_code)
    if not pref_name:
        raise HTTPException(status_code=400, detail="不正な都道府県コードです")

    try:
        gdf = load_split_land_price(pref_name)

        if req.usage:
            gdf = gdf[gdf["用途"] == req.usage]
        if req.structure:
            gdf = gdf[gdf["構造"] == req.structure]

        if gdf.empty:
            raise HTTPException(status_code=404, detail="該当する地価データが見つかりません")

        representative = gdf.iloc[0]

        unit_price = _safe_cast(representative["用途別価格"], 0.0, float)

        return LandPriceDTO(
            location=representative["都道府県名"],
            use=representative["用途"],
            structure=representative.get("構造", None),
            price=unit_price,
            base_price=_safe_cast(representative["地価目安"], 0.0, float),
            factor=_safe_cast(representative["倍率"], 1.0, float),
            year=None,
            distance_m=None,
            source="split",
            total_price=unit_price * req.area if req.area else None
        )

    except Exception as e:
        logger.exception("地価データ取得処理でエラーが発生しました")
        raise HTTPException(status_code=500, detail="地価データの取得に失敗しました")


   #logger.info(f"地価取得リクエスト: pref_code: {pref_code}")
   #lat={lat}, lon={lon}, 
   # 現行年度読み込み
   #try:
   #    gdf = load_land_price_data(pref_code)
    #   if gdf.empty:
   #        raise FileNotFoundError("現行データなし")
   #    source = "current"
   #except FileNotFoundError:
   #    logger.warning(f"現行年度データなし → 過去年度データ検索へ：pref_code: {pref_code}")
    #   try:
    #       gdf = load_old_land_price_data(pref_code)
    ##           raise HTTPException(status_code=404, detail="過去年度含めて地価データなし")
     #      source = "old"
     #  except FileNotFoundError:
    #       logger.error(f"地価データが一切見つかりません: pref_code: {pref_code}")
    #       raise HTTPException(status_code=404, detail="地価データが見つかりません")
    #   except Exception as e:
    #       logger.exception(f"過去年度データ読み込みエラー: {e}")
    #       raise HTTPException(status_code=500, detail="過去年度地価データ読み込み失敗")
  # except Exception as e:
  #     logger.exception(f"現行データ読み込みエラー: {e}")
  #     raise HTTPException(status_code=500, detail="地価データ読み込み失敗")
   # 距離計算と最寄点検索
  # try:
       #target = (lat, lon)
   #    gdf = gdf.to_crs(epsg=4326) if hasattr(gdf, "crs") else gdf
   #    gdf["distance"] = gdf.geometry.apply(lambda geom: geodesic((geom.y, geom.x)).meters)
   #    nearest = gdf.loc[gdf["distance"].idxmin()]
   #except Exception as e:
       #logger.exception(f"最寄点検索エラー（lat={lat}, lon={lon}）: {e}")
   #    raise HTTPException(status_code=500, detail="地価データ解析に失敗しました")
   # DTO整形
  # return LandPriceDTO(
   #    location=_safe_cast(nearest.get("L01_001"), "", str),
   #    price=_safe_cast(nearest.get("L01_006"), 0.0, float),
  #     use=_safe_cast(nearest.get("L01_003"), "", str),
  #     year=_safe_cast(nearest.get("L01_002"), None, int),
  #     distance_m=round(_safe_cast(nearest["distance"], 0.0, float), 1),
  #     source=source
  # )