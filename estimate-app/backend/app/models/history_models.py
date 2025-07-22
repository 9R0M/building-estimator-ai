#estimate-app\backend\app\models\history_models.py
from datetime import datetime
from app.models.estimate_models import EstimateRequest, EstimateResponse
from pydantic import BaseModel


class HistoryRecord(BaseModel):
    id: int
    request: EstimateRequest
    response: EstimateResponse
    timestamp: datetime