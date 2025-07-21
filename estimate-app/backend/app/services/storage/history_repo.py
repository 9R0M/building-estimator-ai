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

# TODO: クラス定義、関数実装をする
class HistoryRepository():
    def __init__(self) -> None:
        pass
    
    def save(self, record: HistoryRecord)-> None:
        return None
    
    def list_all(self) -> List[HistoryRecord]:
        return []