# === app/services/logic/land_price_service.py ===
from abc import ABC, abstractmethod
from app.models.land_price_dto import LandPriceDTO

class ILandPriceRepository(ABC):
    @abstractmethod
    def find_nearest(self, lat: float, lon: float, pref_code: str) -> LandPriceDTO:
        ...

# TODO: 関数実装をする
class LandPriceRepository(ILandPriceRepository):
    def __init__(self, data_dir: str) -> None:
        pass

    def find_nearest(self, lat: float, lon: float, pref_code: str) -> LandPriceDTO:
        return LandPriceDTO(
            location="",
            price=0.0,
            distance_m=0.0
        )