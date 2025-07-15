import { BrowserRouter, Route, Routes } from "react-router-dom";
import EstimatePage from "./pages/EstimatePage";
import TopPage from "./pages/Toppage";

type LineItem = {
  description: string;
  quantity: number;
  unitPrice: number;
};

// ネストされた JSON 構造の型定義
type BuildingInfo = {
  structure: string;
  usage: string;
  floors: number;
  building_age: number;
  area: number;
};
type LocationInfo = {
  lat: number;
  lon: number;
  pref_code: string;
};
type EstimateWithLocationRequest = {
  building: BuildingInfo;
  location: LocationInfo;
};

type EstimateState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; estimate: number }
  | { status: "error"; message: string };

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<TopPage />} />
        <Route path="/estimate" element={<EstimatePage />} />
      </Routes>
    </BrowserRouter>
  )
}