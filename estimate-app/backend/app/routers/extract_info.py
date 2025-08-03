from fastapi import APIRouter, UploadFile, File, HTTPException
import pytesseract, cv2, numpy as np, re

from app.models.estimate_models import EstimateRequest
router = APIRouter(prefix="/api/extract", tags=["extract"])
@router.post("/", response_model=EstimateRequest, summary="OCRで建物情報を抽出")
async def extract_info(file: UploadFile = File(...)):
   contents = await file.read()
   if not contents:
       raise HTTPException(status_code=400, detail="ファイルが空です")
   nparr = np.frombuffer(contents, np.uint8)
   img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
   if img is None:
       raise HTTPException(status_code=400, detail="画像読み込みに失敗しました")
   gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
   text = pytesseract.image_to_string(gray, lang='jpn+eng')
   structure = "RC" if re.search(r"RC|鉄筋", text) else ("S" if re.search(r"S造", text) else ("木造" if re.search(r"木造", text) else ""))
   floors_match = re.search(r"(?:地上|地下)?(\d+)階", text)
   floors = int(floors_match.group(1)) if floors_match else 0
   area_match = re.search(r"(\d{2,4}(?:\.\d+)?)(?:㎡|m2)", text)
   area = float(area_match.group(1)) if area_match else 0.0
   return EstimateRequest(
       structure=structure,
       floors=floors,
       area=area,
       usage="", building_age=0,
       lat=0.0, lon=0.0, pref_code=""
   )