# === app/services/logic/land_price_service.py ===
from abc import ABC, abstractmethod
from app.models.land_price_dto import LandPriceDTO

class ILandPriceRepository(ABC):
    @abstractmethod
    def find_nearest(self, lat: float, lon: float, pref_code: str) -> LandPriceDTO:
        ...

class LandPriceRepository(ILandPriceRepository):
    def __init__(self, data_dir: str) -> None:
        pass

    def find_nearest(self, lat: float, lon: float, pref_code: str) -> LandPriceDTO:
        return super().find_nearest(lon, pref_code)