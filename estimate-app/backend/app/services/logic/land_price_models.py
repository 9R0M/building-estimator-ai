# backend/app/routers/land_price.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import os
import geopandas as gpd
from app.models.estimate_models import LandPriceDTO

router = APIRouter(prefix="/land-price", tags=["land-price"])
logger = logging.getLogger(__name__)

# ---------- パス設定 ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPLIT_DIR = os.path.normpath(os.path.join(BASE_DIR, "../../script/data/land_price/split"))

# ---------- 都道府県コード → 名称 ----------
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

# ---------- リクエストモデル ----------
class LandPriceRequest(BaseModel):
    pref_code: str

# ---------- データ読込 ----------
def load_land_price_data(pref_code: str) -> gpd.GeoDataFrame:
    pref_name = PREF_CODE_TO_NAME.get(pref_code)
    if not pref_name:
        raise ValueError(f"不正な都道府県コード: {pref_code}")
    
    path = os.path.join(SPLIT_DIR, f"{pref_name}.parquet")
    if not os.path.exists(path):
        logger.warning(f"地価ファイルが見つかりません: {path}")
        raise FileNotFoundError(path)
    
    return gpd.read_parquet(path)

# ---------- 安全キャスト ----------
def _safe_cast(value, default, cast):
    try:
        return cast(value) if value is not None else default
    except (ValueError, TypeError):
        return default

# ---------- POSTエンドポイント ----------
@router.post("/", response_model=LandPriceDTO, summary="代表地価を取得（POST）")
async def get_land_price(req: LandPriceRequest):
    logger.info(f"地価取得 req: {req}")
    source = "split"

    try:
        gdf = load_land_price_data(req.pref_code)
        # sort_values の結果を別変数にして明示せず使う
        representative = gdf.sort_values(by="L01_006").iloc[len(gdf) // 2]

        if gdf.empty:
            raise ValueError("地価データが空です")
        path = "script/data/land_price/split/東京都.parquet" 
        gdf = gpd.read_parquet(path)
        gdf: gpd.GeoDataFrame = gdf  # 明示してPylance黙らせる

        representative = gdf.sort_values("L01_006").iloc[len(gdf) // 2]

    except Exception as e:
        logger.exception(f"地価データ取得エラー: {e}")
        raise HTTPException(status_code=500, detail="地価データ取得に失敗しました")

    return LandPriceDTO(
        location=_safe_cast(representative.get("L01_001"), "", str),
        price=_safe_cast(representative.get("L01_006"), 0.0, float),
        use=_safe_cast(representative.get("L01_003"), "", str),
        year=_safe_cast(representative.get("L01_002"), None, int),
        distance_m=None,
        source=source
    )
