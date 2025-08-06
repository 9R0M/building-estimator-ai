// src/pages/AllInOneEstimatePage.tsx
import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import styles from "../styles/AllInOneEstimatePage.module.css";
import UploadSection from "../components/UploadSection";
import { useItems } from "../hooks/useItemsReducer";
import { prefectures, type Prefecture } from "../utils/prefectures";
import SelectTypeMenu from "../components/SelectTypeMenu";
import NumberInputTypeMenu from "../components/NumberInputTypeMenu";
import type { LandPriceResponse, EstimateResponse, OcrResponse } from "../types/api";
//import { serverUrl } from "../local.env";
type FileWithPreview = File & { preview: string };

const MAX_FILES = 10;
const serverUrl = import.meta.env.VITE_SERVER_URL;

const AllInOneEstimatePage: React.FC = () => {
    const [prefCode, setPrefCode] = useState("");
    const [landPrice, setLandPrice] = useState<number | null>(null);
    const [landPriceLoading, setLandPriceLoading] = useState(false);
    const [errorPref] = useState("");
    const [loading, setLoading] = useState(false);
    const [files, setFiles] = useState<FileWithPreview[]>([]);
    const { items, change, add, remove, isValid, dispatch } = useItems();
    const [estimate, setEstimate] = useState<number | null>(null);
    const [lastAction, setLastAction] = useState<string | null>(null);
    const [ocrText, setOcrText] = useState("");
    const [structure, setStructure] = useState("RC");
    const [floors, setFloors] = useState(1);
    const [yearOfConstruction, setYearOfConstruction] = useState(0);
    const [area, setArea] = useState(0);
    const [usage, setUsage] = useState("ビル");
    const structures = [
        { label: "RC", value: "RC" },
        { label: "SRC", value: "SRC" },
        { label: "S", value: "S" }
    ];
    const usages = [
        { label: "ビル", value: "ビル" },
        { label: "住宅", value: "住宅" },
        { label: "オフィス", value: "オフィス" },
        { label: "工場", value: "工場" },
        { label: "学校", value: "学校" },
        { label: "商業施設", value: "商業施設" },
        { label: "病院", value: "病院" },
        { label: "その他", value: "その他" }
    ];
    const totalItemsCost = items.reduce((sum, it) => sum + it.quantity * it.unitPrice, 0);
    const total = totalItemsCost + (landPrice ?? 0);
    const validatePref = (_v: string): boolean => {
        return true;
    };
    const historyBuffer = {
        add: (record: any) => {
            localStorage.setItem("lastEstimate", JSON.stringify(record));
        }
    };
    const wrapperSetFiles = (updater: (prev: FileWithPreview[]) => FileWithPreview[]) => {
        setFiles(updater);
    };
    useEffect(() => {
        if (lastAction === "SUBMIT") {
            historyBuffer.add({ timestamp: Date.now(), items });
            axios
                .post(
                    serverUrl + "/api/add_sample_batch",
                    {
                        samples: items.map(it => ({
                            features: { area: it.unitPrice, rooms: it.quantity },
                            actual: it.quantity * it.unitPrice,
                        })),
                    },
                    { headers: { "x-api-version": "2" } }
                )
                .catch(_err => toast.error("学習データ送信に失敗しました"));
            setLastAction(null);
        }
    }, [lastAction, items]);
    const landPriceCtrl = useRef<AbortController | null>(null);
    const handleLandPriceFetch = async () => {
        if (!validatePref(prefCode)) return;
        setLandPriceLoading(true);
        toast.info("地価取得中…");
        landPriceCtrl.current?.abort();
        const ctrl = new AbortController();
        landPriceCtrl.current = ctrl;
        const req = { pref_code: prefCode };
        try {
            const r = await axios.post<LandPriceResponse>(
                `${serverUrl}/api/land-price/`,
                req, // ✅ POSTボディ
                { signal: ctrl.signal }
            );
            console.log(r.data);

            if (r.data.base_price === null) {
                toast.error("地価が取得できませんでした")
            } else {
                setLandPrice(r.data.base_price);
                toast.success("地価を取得しました");
            }
        } catch (e: any) {
            if (!axios.isCancel(e)) toast.error(`地価取得エラー: ${e.message}`);
            console.log(e);
        } finally {
            setLandPriceLoading(false);
        }
    };
    const ocrCtrl = useRef<AbortController | null>(null);
    const handleOcrUpload = async () => {
        ocrCtrl.current?.abort();
        const ctrl = new AbortController();
        ocrCtrl.current = ctrl;
        const form = new FormData();
        files.forEach(f => form.append("files", f));
        toast.info("OCR解析中…");
        try {
            const r = await axios.post<OcrResponse>(`${serverUrl}/api/extract-info`, form, { signal: ctrl.signal });
            setOcrText(r.data.text);
            toast.success("OCR解析完了");
        } catch (e: any) {
            if (!axios.isCancel(e)) toast.error(`OCRエラー: ${e.message}`);
        }
    };
    const handleEstimate = async () => {
        setLoading(true);
        const form = new FormData();
        files.forEach(f => form.append("files", f));
        const req = {
            structure: structure,
            area: area,
            floors: floors,
            usage: usage,
            building_age: yearOfConstruction,
            pref_code: prefCode,
        };
        form.append( //使ってない
            "payload",
            new Blob([JSON.stringify(req/*, items }*/)], {
                type: "application/json",
            })
        );

        try {
            const ctrl = new AbortController();
            //console.log(req);
            const r = await axios.post<EstimateResponse>(
                `${serverUrl}/api/estimate/`,
                req,
                { signal: ctrl.signal }
            );
            const cost = r.data.estimated_amount;
            setEstimate(cost);
            console.log(`estimate: ${estimate}`);
            dispatch({ type: "SUBMIT" });
            setLastAction("SUBMIT");
            toast.success("見積完了");
        } catch (e: any) {
            toast.error("見積りに失敗しました: " + e.message);
        }
        setLoading(false);
    };
    const downloadPDF = () => estimate != null && window.open(`/auto-estimate/${estimate}/history.pdf`);
    const downloadExcel = () => estimate != null && window.open(`/auto-estimate/${estimate}/history.xlsx`);
    return (
        <div className={styles.container} role="main">
            <ToastContainer position="bottom-right" autoClose={3000} />
            <h1>見積システム</h1>
            <section className={styles.section} aria-labelledby="land-price">
                <h2 id="land-price">地価取得</h2>
                <form onSubmit={e => { e.preventDefault(); handleLandPriceFetch(); }}> {/* */}
                    <div className={styles.formGroup}>
                        <label htmlFor="pref-select">都道府県を選択（必須）</label>
                        <select
                            id="pref-select"
                            value={prefCode}
                            onChange={e => setPrefCode(e.target.value)}
                        >
                            <option value="">選択してください</option>
                            {prefectures.map((p: Prefecture) => (
                                <option key={p.code} value={p.code}>
                                    {p.label}
                                </option>
                            ))}
                        </select>
                        {errorPref && (
                            <p className={styles.errorMessage} role="alert">
                                {errorPref}
                            </p>
                        )}
                    </div>
                    <button type="submit" disabled={landPriceLoading}>
                        {landPriceLoading ? "取得中…" : "地価取得"}
                    </button>
                </form>
                {landPrice != null && (
                    <p>地価：<strong>{landPrice.toLocaleString()} 円/㎡</strong></p>
                )}
            </section>
            <SelectTypeMenu label="構造" selectList={structures} value={structure} onChange={setStructure} />
            <NumberInputTypeMenu label="階数" state={floors} setState={setFloors} />
            <NumberInputTypeMenu label="築年数" state={yearOfConstruction} setState={setYearOfConstruction} />
            <NumberInputTypeMenu label="面積" state={area} setState={setArea} />
            <SelectTypeMenu label="用途" selectList={usages} value={usage} onChange={setUsage} />
            <section className={styles.section} aria-labelledby="ocr-section">
                <h2 id="ocr-section">図面 &amp; OCR（任意・最大{MAX_FILES}枚）</h2>
                <UploadSection files={files} setFiles={wrapperSetFiles} />
                <button type="button" onClick={handleOcrUpload} disabled={files.length === 0}>
                    OCR解析
                </button>
                {ocrText && (
                    <pre className={styles.ocrText} aria-live="polite" aria-atomic="true">
                        {ocrText}
                    </pre>
                )}
            </section>
            <section className={styles.section} aria-labelledby="items-section">
                <h2 id="items-section">明細入力</h2>
                <form onSubmit={e => e.preventDefault()}>
                    {items.map((it, i) => (
                        <fieldset key={i} className={styles.itemRow} aria-labelledby={`item-${i}-legend`}>
                            <legend id={`item-${i}-legend`}>項目 {i + 1}</legend>
                            <label>
                                内容
                                <input
                                    required
                                    type="text"
                                    placeholder="内容"
                                    value={it.description}
                                    onChange={e => change(i, "description", e.target.value)}
                                />
                            </label>
                            <label>
                                数量
                                <input
                                    required
                                    type="number"
                                    placeholder="数量"
                                    min="0"
                                    value={it.quantity}
                                    onChange={e => change(i, "quantity", +e.target.value)}
                                />
                            </label>
                            <label>
                                単価
                                <input
                                    required
                                    type="number"
                                    placeholder="単価"
                                    min="0"
                                    value={it.unitPrice}
                                    onChange={e => change(i, "unitPrice", +e.target.value)}
                                />
                            </label>
                            <span aria-label={`合計金額：${it.quantity * it.unitPrice} 円`}>
                                {(it.quantity * it.unitPrice).toLocaleString()} 円
                            </span>
                            <button type="button" onClick={() => remove(i)}>削除</button>
                        </fieldset>
                    ))}
                    <button type="button" onClick={add}>＋ 行追加</button>
                </form>
                <p>明細合計：<strong>{total.toLocaleString()}</strong> 円</p>
            </section>
            <section className={styles.section} aria-labelledby="estimate-section">
                <h2 id="estimate-section">見積結果</h2>
                <p>小計：<strong>{total.toLocaleString()}</strong> 円</p>
                <button type="button" onClick={handleEstimate} disabled={loading}>
                    {loading ? "実行中…" : "見積り実行"}
                </button>
                {estimate != null && (
                    <div className={styles.result} role="region" aria-live="polite" aria-atomic="true">
                        <p>合計：<strong>{estimate.toLocaleString()} 円</strong></p>
                        <button type="button" onClick={downloadPDF}>PDFダウンロード</button>
                        <button type="button" onClick={downloadExcel}>Excelダウンロード</button>
                    </div>
                )}
            </section>
        </div>
    );
};
export default AllInOneEstimatePage;