import React, { useState, type DragEvent, useEffect } from "react";
import styles from "../styles/TopPage.module.css";
import axios from "axios";
interface Item {
  description: string;
  quantity: number;
  unitPrice: number;
}
const TopPage: React.FC = () => {
  const [prefCode, setPrefCode] = useState("");
  const [postalCode, setPostalCode] = useState("");
  const [address, setAddress] = useState("");
  const [landPrice, setLandPrice] = useState<number | null>(null);
  const [landPriceLoading, setLandPriceLoading] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [dragActive, setDragActive] = useState(false);
  // エラーメッセージ用ステート
  const [errorPref, setErrorPref] = useState("");
  const [errorPostal, setErrorPostal] = useState("");
  const [errorAddress, setErrorAddress] = useState("");
  const [errorSubmit, setErrorSubmit] = useState("");
  const [items, setItems] = useState<Item[]>([
    { description: "", quantity: 1, unitPrice: 0 }
  ]);
  const [errorItems, setErrorItems] = useState<string[]>([]);
  const total = items.reduce((sum, i) => sum + i.quantity * i.unitPrice, 0);
  const validatePref = (val: string) => {
    if (!val) setErrorPref("都道府県を選択してください");
    else setErrorPref("");
  };
  const validatePostal = (val: string) => {
    if (val && !/^\d{7}$/.test(val)) {
      setErrorPostal("郵便番号は7桁で入力してください");
    } else {
      setErrorPostal("");
    }
  };
  const handlePrefChange = (val: string) => {
    setPrefCode(val);
    validatePref(val);
  };
  const handlePostalChange = (val: string) => {
    setPostalCode(val);
    validatePostal(val);
  };
  const handlePostalSearch = async () => {
    validatePostal(postalCode);
    if (errorPostal) return;
    try {
      const res = await axios.get(`https://api.zipaddress.net/?zipcode=${postalCode}`);
      if (res.data?.code === 200) {
        setAddress(res.data.data.fullAddress);
        setErrorAddress("");
        await fetchLandPrice(res.data.data.fullAddress);
      } else {
        setErrorAddress("住所取得できませんでした");
      }
    } catch {
      setErrorAddress("住所検索に失敗しました");
    }
  };
  const fetchLandPrice = async (addr: string) => {
    validatePref(prefCode);
    if (!prefCode) return;
    setLandPriceLoading(true);
    try {
      const res = await axios.post('/api/land-price', {
        pref_code: prefCode,
        address: addr,
      });
      if (res.data?.land_price) {
        setLandPrice(res.data.land_price);
        setErrorSubmit("");
      } else {
        setErrorSubmit("地価取得できませんでした");
      }
    } catch (err) {
      console.error(err);
      setErrorSubmit("地価取得に失敗しました");
    } finally {
      setLandPriceLoading(false);
    }
  };
  const onFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const arr = Array.from(e.target.files).filter(f => f.type.startsWith("image/"));
    setFiles(prev => [...prev, ...arr]);
  };
  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragActive(false);
    const arr = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith("image/"));
    setFiles(prev => [...prev, ...arr]);
  };
  const removeFile = (i: number) => setFiles(prev => prev.filter((_, idx) => idx !== i));
  const validateItems = (its: Item[]) => {
    const errs = its.map(it =>
      it.description && it.quantity > 0 && it.unitPrice >= 0 ? "" : "項目・数量・単価を正しく入力してください"
    );
    setErrorItems(errs);
    return errs.every(e => !e);
  };
  const handleItemChange = (idx: number, key: keyof Item, val: string | number) => {
    setItems(prev => {
      const c = [...prev];
      (c[idx] as any)[key] = val;
      validateItems(c);
      return c;
    });
  };
  const addItem = () => {
    setItems(prev => [...prev, { description: "", quantity: 1, unitPrice: 0 }]);
    setErrorItems(prev => [...prev, "項目名を入力してください"]);
  };
  const removeItem = (i: number) => {
    setItems(prev => prev.filter((_, idx) => idx !== i));
    setErrorItems(prev => prev.filter((_, idx) => idx !== i));
  };
  const handleSubmit = async () => {
    validatePref(prefCode);
    if (errorPref) return;
    if (!validateItems(items)) return;
    const form = new FormData();
    form.append("prefCode", prefCode);
    form.append("postalCode", postalCode);
    form.append("address", address);
    form.append("landPrice", String(landPrice ?? ""));
    form.append("items", JSON.stringify(items));
    files.forEach(f => form.append("files", f));
    try {
      await axios.post('/api/estimate', form, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      alert("見積送信成功!");
    } catch (err) {
      console.error(err);
      setErrorSubmit("見積送信失敗");
    }
  };
  return (
    <div className={styles.container}>
      <h1>建築・地価 見積システム</h1>
      <div className={styles.formGroup}>
        <label htmlFor="pref">都道府県</label>
        <select id="pref" value={prefCode} onChange={e => handlePrefChange(e.target.value)} onBlur={() => validatePref(prefCode)}>
          <option value="">選択してください</option>
          <option value="13">東京都</option>
          <option value="14">神奈川県</option>
          {/* 他の都道府県も */}
        </select>
        {errorPref && <p className={styles.errorMessage}>{errorPref}</p>}
      </div>
      <div className={styles.formGroup}>
        <label htmlFor="postal">郵便番号</label>
        <div style={{ display: "flex", gap: 8 }}>
          <input id="postal" value={postalCode} onChange={e => handlePostalChange(e.target.value)} onBlur={() => validatePostal(postalCode)} placeholder="1000001" />
          <button type="button" onClick={handlePostalSearch}>住所取得＆地価取得</button>
        </div>
        {errorPostal && <p className={styles.errorMessage}>{errorPostal}</p>}
        {errorAddress && <p className={styles.errorMessage}>{errorAddress}</p>}
      </div>
      {address && <p>住所: {address}</p>}
      {landPrice !== null && <p>推定地価: {landPrice.toLocaleString()} 円/㎡</p>}
      {errorSubmit && <p className={styles.errorMessage}>{errorSubmit}</p>}
      {/* 他の入力項目（画像、明細など）省略せず続けて配置 */}
      <button className={styles.nextButton} onClick={handleSubmit}>見積送信</button>
    </div>
  );
};
export default TopPage;