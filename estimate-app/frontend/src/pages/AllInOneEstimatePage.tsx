// src/pages/AllInOneEstimatePage.tsx
import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import styles from "../styles/AllInOneEstimatePage.module.css";
import UploadSection from "../components/UploadSection";
import { useItems, type Item } from "../hooks/useItemsReducer";
import { prefectures } from "../utils/prefectures.ts";

type FileWithPreview = File & { preview: string };
type EstimateResponse = { estimated_cost: number | null };
type LandPriceResponse = { land_price: number | null };
type OcrResponse = { text: string };

const MAX_FILES = 10;

const AllInOneEstimatePage: React.FC = () => {
    const [prefCode, setPrefCode] = useState("");
    const [landPrice, setLandPrice] = useState<number | null>(null);
    const [landPriceLoading, setLandPriceLoading] = useState(false);
    const [errorPref, setErrorPref] = useState("");
    const [loading, setLoading] = useState(false);
    const [files, setFiles] = useState<FileWithPreview[]>([]);
    const { items, change, add, remove, isValid, dispatch } = useItems();
    const [estimate, setEstimate] = useState<number | null>(null);
    const [lastAction, setLastAction] = useState<string | null>(null);
    const [ocrText, setOcrText] = useState("");

    const totalItemsCost = items.reduce((sum, it) => sum + it.quantity * it.unitPrice, 0);
    const total = totalItemsCost + (landPrice ?? 0);

    const validatePref = (v: string): boolean => {
        if (!v) {
            toast.error("都道府県を選択してください");
            return false;
        }
        return true;
    };

    const historyBuffer = {
        add: (record: any) => {
            // ここでは localStorage を利用
            // 必ず文字列化（JSON.stringify）して保存する必要があります
            localStorage.setItem("lastEstimate", JSON.stringify(record));
        }
    };

    const wrapperSetFiles = (updater: (prev: FileWithPreview[]) => FileWithPreview[]) => {
        setFiles(updater);
    };

    const removeFile = (idx: number) => {
        setFiles(prev => {
            URL.revokeObjectURL(prev[idx].preview);
            return prev.filter((_, i) => i !== idx);
        });
    };
    useEffect(() => {
        // 一回限りの SUBMIT トリガー処理
        if (lastAction === "SUBMIT") {
            // ① 履歴を IndexedDB/LocalStorage に追加（擬似コード）
            historyBuffer.add({ timestamp: Date.now(), items });

            // ② 継続学習用AIに Experience Replay を送信
            axios
                .post(
                    "/api/add_sample_batch",
                    {
                        samples: items.map(it => ({
                            features: { area: it.unitPrice, rooms: it.quantity },
                            actual: it.quantity * it.unitPrice,
                        })),
                    },
                    { headers: { "x-api-version": "2" } }
                )
                .catch(err => toast.error("学習データ送信に失敗しました"));

            // ✅ 一回限りにするためトリガーをリセット
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
        try {
            const r = await axios.post<LandPriceResponse>(
                "/api/land-price",
                { pref_code: prefCode },
                { signal: ctrl.signal }
            );
            setLandPrice(r.data.land_price);
            r.data.land_price == null
                ? toast.error("地価が取得できませんでした")
                : toast.success("地価を取得しました");
        } catch (e: any) {
            if (!axios.isCancel(e)) toast.error(`地価取得エラー: ${e.message}`);
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
            const r = await axios.post<OcrResponse>("/extract-info", form, { signal: ctrl.signal });
            setOcrText(r.data.text);
            toast.success("OCR解析完了");
        } catch (e: any) {
            if (!axios.isCancel(e)) toast.error(`OCRエラー: ${e.message}`);
        }
    };
    const estimateCtrl = useRef<AbortController | null>(null);

    const handleEstimate = async () => {
        if (!validatePref(prefCode) || !isValid()) return;
        setLoading(true);

        const form = new FormData();
        files.forEach(f => form.append("files", f));
        form.append(
            "payload",
            new Blob([JSON.stringify({ pref_code: prefCode, items })], {
                type: "application/json",
            })
        );

        try {
            const r = await axios.post<EstimateResponse>("/api/auto-estimate", form);
            setEstimate(r.data.estimated_cost);

            // ✅ 成功したら SUBMIT を dispatchしてトリガーにセット
            dispatch({ type: "SUBMIT" });
            setLastAction("SUBMIT");
            toast.success("見積完了");
        } catch (e: any) {
            toast.error("見積りに失敗しました: " + e.message);
        } finally {
            setLoading(false);
        }
    };

    const downloadPDF = () => estimate != null && window.open(`/auto-estimate/${estimate}/history.pdf`);
    const downloadExcel = () => estimate != null && window.open(`/auto-estimate/${estimate}/history.xlsx`);
    return (
        <div className={styles.container}>
            <ToastContainer position="bottom-right" autoClose={3000} />
            <h1>見積システム</h1>
            {/* 地価取得 */}
            <section className={styles.section}>
                <h2>地価取得</h2>
                <div className={styles.formGroup}>
                    <select value={prefCode} onChange={e => setPrefCode(e.target.value)}>
                        <option value="">選択してください</option>
                        {prefectures.map(p => <option key={p.code} value={p.code}>{p.name}</option>)}
                    </select>
                    {errorPref && <p className={styles.errorMessage}>{errorPref}</p>}
                </div>
                <button onClick={handleLandPriceFetch} disabled={landPriceLoading}>
                    {landPriceLoading ? "取得中…" : "地価取得"}
                </button>
                {landPrice != null && <p>地価: {landPrice.toLocaleString()} 円/㎡</p>}
            </section>
            {/* 図面 & OCR 任意 */}
            <section className={styles.section}>
                <h2>図面 & OCR（任意・最大{MAX_FILES}枚）</h2>
                <UploadSection files={files} setFiles={wrapperSetFiles} />
                <div className={styles.previews}>
                    {files.map((f, i) => (
                        <div key={i} className={styles.previewItem}>
                            <img src={f.preview} alt={f.name} width={100} />
                            <button onClick={() => removeFile(i)}>×</button>
                        </div>
                    ))}
                </div>
                <button onClick={handleOcrUpload} disabled={files.length === 0}>
                    OCR解析
                </button>
                {ocrText && <pre className={styles.ocrText}>{ocrText}</pre>}
            </section>
            {/* 明細入力セクション */}
            <section className={styles.section}>
                <h2>明細入力</h2>
                {items.map((it: Item, i: number) => (
                    <div key={i} className={styles.itemRow}>
                        <input
                            placeholder="内容"
                            value={it.description}
                            onChange={e => change(i, "description", e.target.value)}
                        />
                        <input
                            type="number"
                            placeholder="数量"
                            value={it.quantity}
                            onChange={e => change(i, "quantity", +e.target.value)}
                        />
                        <input
                            type="number"
                            placeholder="単価"
                            value={it.unitPrice}
                            onChange={e => change(i, "unitPrice", +e.target.value)}
                        />
                        <span>{(it.quantity * it.unitPrice).toLocaleString()} 円</span>
                        <button onClick={() => remove(i)}>削除</button>
                    </div>
                ))}
                <button onClick={add}>＋ 行追加</button>
                <p>明細合計：{total.toLocaleString()} 円</p>
            </section>

            {/* 見積り実行セクション */}
            <section className={styles.section}>
                <h2>見積結果</h2>
                <p>小計: {total.toLocaleString()} 円</p>
                <button onClick={handleEstimate} disabled={loading}>
                    {loading ? "実行中…" : "見積り実行"}
                </button>
                {estimate != null && (
                    <div className={styles.result}>
                        <p>
                            合計：<strong>{estimate.toLocaleString()} 円</strong>
                        </p>
                    </div>
                )}
            </section>
        </div>
    );
};
export default AllInOneEstimatePage;