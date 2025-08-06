export type LandPriceResponse = {
  location: string;           // 都道府県名（例：東京都）
  use: string;               // 用途（例：住宅、ビル、病院）
  stringucture: string | null;   // ← NEW: RC, SRC, Sなど
  price: number;            // 用途別価格（地価 × 倍率）
  base_price: number | null;  // 元の地価目安（オプション）
  factor: number | null;      // 倍率（オプション）
  year: number | null;          // 年度（未使用ならNone）
  distance_m: number | null;  // 未使用（将来GPS用）
  source: string | null;       // データソース（例：split）
  total_price: number | null;   // 面積を掛けた合計
};

export type EstimateResponse = {
  estimated_cost: number | null;
};

export type OcrResponse = {
  text: string;
};
