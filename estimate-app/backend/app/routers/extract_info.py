# estimate_logic/extract_info.py
from pydantic import BaseModel, Field
from fastapi import UploadFile, HTTPException
import pytesseract, cv2, numpy as np, re
from typing import Optional, Tuple
class ExtractedResult(BaseModel):
   structure: Optional[str] = Field(None, description="建物構造")
   floors: Optional[int] = Field(None, description="階数")
   area: Optional[float] = Field(None, description="面積（㎡）")
   raw_text: Optional[str] = Field(None, description="OCR抽出テキスト")
   processed_image_shape: Optional[Tuple[int,int]] = Field(None, description="前処理後画像のサイズ")
def extract_info_from_blueprint(file: UploadFile) -> ExtractedResult:
   contents = file.file.read()

   if not contents:
       raise HTTPException(status_code=400, detail="ファイルが空です")
   
   nparr = np.frombuffer(contents, np.uint8)
   img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

   if img is None:
       raise HTTPException(status_code=400, detail="画像読み込みに失敗しました")
   
   gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
   blur = cv2.medianBlur(gray, 3)
   h, w = blur.shape
   clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
   enhanced = clahe.apply(blur)
   _, bw = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
   pad = 10
   padded = cv2.copyMakeBorder(bw, pad,pad,pad,pad, cv2.BORDER_CONSTANT, value=255)
   text = pytesseract.image_to_string(padded, config="--psm 6 -l jpn+eng")
   structure = None

   if re.search(r"RC|鉄筋", text): structure="RC"
   elif re.search(r"S造", text): structure="S"
   elif re.search(r"木造", text): structure="木造"

   floors = None
   flm = re.search(r"(?:地上|地下)?(\d+)階", text)

   if flm: floors = int(flm.group(1))

   area = None
   am = re.search(r"(\d{2,4}(?:\.\d+)?)(?:㎡|平方メートル|平米|m2|sq\s?m)", text)

   if am: area = float(am.group(1))
   
   return ExtractedResult(
       structure=structure,
       floors=floors,
       area=area,
       raw_text=text,
       processed_image_shape=(h+pad*2, w+pad*2),
   )