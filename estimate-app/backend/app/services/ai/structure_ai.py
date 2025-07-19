# === app/services/ai/structure_ai.py ===
# TextResult を定義しているモデルがある場合、それも import
# 例: from app.models.ocr_models import TextResult

class StructureAI():
    def predict(self, text: TextResult):
        return StructureResult