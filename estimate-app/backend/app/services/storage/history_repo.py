# === app/services/storage/history_repo.py ===
from abc import ABC, abstractmethod
from typing import List
from app.models.history_models import HistoryRecord

class IHistoryRepository(ABC):
    @abstractmethod
    def save(self, record: HistoryRecord)-> None:
        ...
    @abstractmethod
    def list_all() -> List[HistoryRecord]:
        ...

class HistoryRepository():
    def __init__(self) -> None:
        pass
    
    def save(self, record: HistoryRecord)-> None:
        return None
    
    def list_all() -> List[HistoryRecord]:
        pass