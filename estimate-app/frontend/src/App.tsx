//estimate-app/frontend/src/App.tsx
import { BrowserRouter, Route, Routes } from "react-router-dom";
import EstimatePage from "./pages/AllInOneEstimatePage";


export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<EstimatePage />} />
        {/*<Route path="/estimate" element={<EstimatePage />} />*/}
      </Routes>
    </BrowserRouter>
  )
}