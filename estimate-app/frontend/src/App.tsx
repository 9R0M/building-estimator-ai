import { useState } from "react";
import styles from "./styles/App.module.css";
import SelectTypeMenu from "./components/SelectTypeMenu";
import NumberInputTypeMenu from "./components/NumberInputTypeMenu";
import UploadSection from "./components/UploadSection";
import { axoisApi } from "./apis/axiosCreate";

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
 const [structure, setStructure] = useState("RC");
 const [floors, setFloors] = useState(5);
 const [area, setArea] = useState(1000);
 const [usage, setUsage] = useState("オフィス");
 const [items, setItems] = useState<LineItem[]>([
   { description: "", quantity: 1, unitPrice: 0 },
 ]);
 const [building_age, setBuilding_age] = useState(0);
 const [estimateState, setEstimateState] = useState<EstimateState>({
   status: "idle",
 });
 const [imageLoading, setImageLoading] = useState(false);
 const handleItemChange = (
 index: number,
 field: keyof LineItem,
 value: string | number
) => {
 const newItems = [...items];
 if (field === "description") {
   newItems[index][field] = String(value) as LineItem[typeof field];
 } else {
   newItems[index][field] = Number(value) as LineItem[typeof field];
 }
 setItems(newItems);
};
 const handleRemoveItem = (index: number) => {
   setItems(items.filter((_, i) => i !== index));
 };
 const getTotal = () =>
   items.reduce((sum, item) => sum + item.quantity * item.unitPrice, 0);
 const handleEstimate = async () => {
   setEstimateState({ status: "loading" });
   const building = {
    structure: structure,
    floors: floors,
    usage: usage,
    building_age: building_age,
    area: area,
};
  const location: LocationInfo = {
    lat: 35.68,
    lon: 139.76,
    pref_code: "13",
  };
  const payload: EstimateWithLocationRequest = {
    building: building,
    location: location,
  }

 try {
   const res = await axoisApi.post("/estimate-with-location", payload);
   setEstimateState({status: "success", estimate:res.data.estimated_cost});
 } catch (err: any) {
   if (err.response) {
     console.error("Server error:", err.response.status, err.response.data);
     throw new Error(err.response.data.detail || "Estimate failed");
   } else {
     console.error("Network error:", err.message);
     throw err;
   }
 }
};
 const handleImageUpload = async (e: React.FormEvent<HTMLFormElement>) => {
   e.preventDefault();
   const form = e.target as HTMLFormElement;
   const fileInput = form.querySelector("input[type='file']") as HTMLInputElement;
   const files = fileInput?.files;
   if (!files || files.length === 0) return;
   setImageLoading(true);
   try {
     const formData = new FormData();
     for (let i = 0; i < files.length; i++) {
       formData.append("files", files[i]);
     }
     const res = await axoisApi.post(
      "/extract-info/",
       formData,
       {
         headers: {
           "Content-Type": "multipart/form-data",
         },
       }
     );
     console.log("解析結果:", res.data);
     // res.data を setStructure や setFloors に反映する場合はここで
   } catch (error) {
     console.error("画像のアップロードに失敗しました:", error);
   } finally {
     setImageLoading(false);
   }
 };
 const handleAddItem = () => {
 setItems([...items, { description: "", quantity: 1, unitPrice: 0 }]);
};

return (
<div className={styles.container}>
<h1 className={styles.title}>建物見積もりAI</h1>
<SelectTypeMenu
       name="構造"
       selectList={["RC", "SRC", "S"]}
       state={structure}
       setState={setStructure}
     />
<NumberInputTypeMenu name="階数" state={floors} setState={setFloors} />
<NumberInputTypeMenu name="延床面積(m²)" state={area} setState={setArea} />
<SelectTypeMenu
       name="用途"
       selectList={["オフィス", "住宅", "商業施設", "工場", "ビル", "学校"]}
       state={usage}
       setState={setUsage}
     />
<UploadSection imageLoading={imageLoading} handler={handleImageUpload} />
<h2>明細項目</h2>
     {items.map((item, index) => (
<div key={index} className={styles.itemRow}>
<input
           type="text"
           placeholder="内容"
           value={item.description}
           onChange={(e) => handleItemChange(index, "description", e.target.value)}
         />
<input
           type="number"
           placeholder="数量"
           value={item.quantity}
           onChange={(e) => handleItemChange(index, "quantity", e.target.value)}
         />
<input
           type="number"
           placeholder="単価"
           value={item.unitPrice}
           onChange={(e) => handleItemChange(index, "unitPrice", e.target.value)}
         />
<span>{(item.quantity * item.unitPrice).toLocaleString()} 円</span>
<button onClick={() => handleRemoveItem(index)}>削除</button>
</div>
     ))}
<button onClick={handleAddItem}>＋ 行を追加</button>
<div>
       合計金額：<strong>{getTotal().toLocaleString()} 円</strong>
</div>
<button className={styles.button} onClick={handleEstimate}>
       見積もりを実行
</button>
<div className={styles.resultBox}>
       {estimateState.status === "loading" && <p>計算中...</p>}
       {estimateState.status === "success" && (
<p className={styles.success}>
           見積金額：<strong>{estimateState.estimate.toLocaleString()} 円</strong>
</p>
       )}
       {estimateState.status === "error" && (
<p className={styles.error}>{estimateState.message}</p>
       )}
</div>
</div>
 );
}