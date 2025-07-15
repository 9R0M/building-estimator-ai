// src/pages/EstimatePage.tsx
import React, { useState, useEffect, type ChangeEvent } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import styles from "../styles/EstimatePage.module.css";
import { axoisApi } from "../apis/axiosCreate";
// import Select from "../components/SelectTypeMenu";
// import Select from "../components/Select";
import Select from "../components/SelectTypeMenu";
import UploadSection from "../components/UploadSection";
import { MapContainer, TileLayer, Marker, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import NumberInputTypeMenu from "../components/NumberInputTypeMenu";

// ドラッグ＆ドロップされたデータをmapに自動反映するMapPicker
const MapPicker: React.FC<{ position: [number, number]; setPosition: (pos: [number, number]) => void }> = ({ position, setPosition }) => {
    useMapEvents({
        click(e) {
            setPosition([e.latlng.lat, e.latlng.lng]);
        },
    });
    return null;
};
type LineItem = { desc: string; qty: number; unit: number };
type LocationState = { lat: number; lng: number; prefCode: string; postalCode: string; files: File[] };
const EstimatePage: React.FC = () => {
    const { state } = useLocation() as { state?: LocationState };
    const navigate = useNavigate();
    if (!state) {
        navigate("/");
        return null;
    }
    const { prefCode, postalCode } = state;
    const [position, setPosition] = useState<[number, number]>([state.lat, state.lng]);
    const [files, setFiles] = useState<File[]>(state.files);
    // 物件情報
    const [structure, setStructure] = useState("RC");
    const [usage, setUsage] = useState("住宅");
    const [floors, setFloors] = useState(1);
    const [area, setArea] = useState(50);
    const [items, setItems] = useState<LineItem[]>([{ desc: "", qty: 1, unit: 0 }]);
    const [estimate, setEstimate] = useState<number | null>(null);
    const [loading, setLoading] = useState(false);
    const handleItemChange = (i: number, field: keyof LineItem, value: string | number) => {
        setItems(prev =>
            prev.map((item, idx) =>
                idx === i
                    ? {
                        ...item,
                        [field]: value,
                    }
                    : item
            )
        );
    };

    const addItem = () => setItems([...items, { desc: "", qty: 1, unit: 0 }]);
    const removeItem = (i: number) => setItems(items.filter((_, idx) => idx !== i));
    const totalItemsCost = items.reduce((sum, it) => sum + it.qty * it.unit, 0);
    const handleEstimate = async () => {
        setLoading(true);
        try {
            const form = new FormData();
            files.forEach((f) => form.append("files", f));
            const payload = {
                lat: position[0],
                lon: position[1],
                pref_code: prefCode,
                postal_code: postalCode,
                structure,
                usage,
                floors,
                building_age: 0,
                area,
                items,
            };
            form.append("payload", new Blob([JSON.stringify(payload)], { type: "application/json" }));
            const res = await axoisApi.post("/auto-estimate", form, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            setEstimate(res.data.estimated_cost);
        } catch (err) {
            console.error(err);
            alert("見積に失敗しました");
        } finally {
            setLoading(false);
        }
    };

    // PDF/Excelダウンロードへのリンク生成
    const downloadPDF = () => {
        window.open(`/auto-estimate/${estimate}/history.pdf`, "_blank");
    };
    const downloadExcel = () => {
        window.open(`/auto-estimate/${estimate}/history.xlsx`, "_blank");
    };
    // OCR解析
    const [ocrText, setOcrText] = useState("");
    const handleOcrUpload = async (files: File[]) => {
        const form = new FormData();
        files.forEach((f) => form.append("files", f));
        const res = await axoisApi.post("/extract-info", form);
        setOcrText(res.data.text || "");
        // 取得構造／面積等にも反映可能
    };
    return (
        <div className={styles.container}>
            <h1>見積ページ</h1>
            <div className={styles.section}>
                <h2>物件情報</h2>
                <Select
                    label="構造" value={structure} onChange={setStructure}

                    selectList={[
                        { value: "RC", label: "RC" },
                        { value: "S", label: "S" },
                        { value: "木造", label: "木造" },
                    ]}
                />
                <NumberInputTypeMenu label="階数" state={floors} setState={setFloors} />
                <NumberInputTypeMenu label="面積（㎡）" state={area} setState={setArea} />
                <Select
                    label="用途"
                    selectList={[
                        { value: "ビル", label: "ビル" },
                        { value: "オフィス", label: "オフィス" },
                        { value: "商業施設", label: "商業施設" },
                        { value: "工場", label: "工場" },
                        { value: "学校", label: "学校" },
                        { value: "住宅", label: "住宅" },
                        { value: "その他", label: "その他" },
                    ]}
                    value={usage}
                    onChange={setUsage}
                />
                <UploadSection
                    label="図面OＣＲ解析"
                    files={files}
                    onUpload={handleOcrUpload}
                    onFilesChange={(f) => setFiles(f)}
                    onRemoveFile={(i) => setFiles((prev) => prev.filter((_, idx) => idx !== i))}
                />
                {ocrText && (
                    <div className={styles.ocrArea}>
                        <h3>OCR抽出内容</h3>
                        <pre>{ocrText}</pre>
                    </div>
                )}
            </div>
            <div className={styles.section}>
                <h2>位置・地価情報</h2>
                <MapContainer center={position} zoom={13} style={{ height: 300 }}>
                    <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="© OpenStreetMap" />
                    <MapPicker position={position} setPosition={setPosition} />
                    <Marker position={position} />
                </MapContainer>
                <p>緯度 {position[0].toFixed(5)} ／ 経度 {position[1].toFixed(5)}</p>
            </div>
            <div className={styles.section}>
                <h2>明細項目</h2>
                {items.map((it, i) => (
                    <div key={i} className={styles.itemRow}>
                        <input placeholder="内容" value={it.desc} onChange={(e) => handleItemChange(i, "desc", e.target.value)} />
                        <input type="number" placeholder="数量" value={it.qty} onChange={(e) => handleItemChange(i, "qty", e.target.value)} />
                        <input type="number" placeholder="単価" value={it.unit} onChange={(e) => handleItemChange(i, "unit", e.target.value)} />
                        <span>{(it.qty * it.unit).toLocaleString()} 円</span>
                        <button type="button" onClick={() => removeItem(i)}>
                            削除
                        </button>
                    </div>
                ))}
                <button type="button" onClick={addItem}>
                    ＋ 行追加
                </button>
                <div className={styles.total}>明細合計: {totalItemsCost.toLocaleString()} 円</div>
            </div>
            <button className={styles.button} onClick={handleEstimate} disabled={loading}>
                {loading ? "計算中…" : "見積り実行"}
            </button>
            {estimate != null && (
                <div className={styles.result}>
                    <h2>見積結果</h2>
                    <p>合計金額：<strong>{estimate.toLocaleString()} 円</strong></p>
                    <button onClick={downloadPDF}>PDFでダウンロード</button>
                    <button onClick={downloadExcel}>Excelでダウンロード</button>
                </div>
            )}
        </div>
    );
};
export default EstimatePage;