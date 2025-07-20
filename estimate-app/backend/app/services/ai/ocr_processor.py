# === app/services/ai/ocr_processor.py ===
from fastapi import UploadFile
from PIL import Image
# OCR内部ユーティリティ関数:
# def load_image(), def clean_text()

class OCRProcessor():
    def preprocess(self, file: UploadFile):
        return Image