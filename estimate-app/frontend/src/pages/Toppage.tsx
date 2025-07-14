// src/pages/TopPage.tsx
import React, {
 useState,
 DragEvent,
 useEffect,
 ChangeEvent,
} from "react";
import { useNavigate } from "react-router-dom";
import {
 MapContainer,
 TileLayer,
 Marker,
 useMapEvents,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import styles from "../styles/TopPage.module.css";
const TopPage: React.FC = () => {
 const [lat, setLat] = useState(35.68);
 const [lng, setLng] = useState(139.76);
 const [prefCode, setPrefCode] = useState("");
 const [postalCode, setPostalCode] = useState("");
 const [address, setAddress] = useState("");
 const [files, setFiles] = useState<File[]>([]);
 const [dragActive, setDragActive] = useState(false);
 const [canGoNext, setCanGoNext] = useState(false);
 const navigate = useNavigate();
 useEffect(() => {
   setCanGoNext(prefCode !== "" && (files.length > 0));
 }, [prefCode, files.length]);
 // 郵便番号 → 住所自動セット（例：郵便番号API連携）
 useEffect(() => {
   if (/^\d{7}$/.test(postalCode)) {
     fetch(`https://zipcloud.ibsnet.co.jp/api/search?zipcode=${postalCode}`)
       .then(res => res.json())
       .then(json => {
         if (json.results?.[0]) {
           const r = json.results[0];
           setAddress(`${r.address1}${r.address2}${r.address3}`);
         }
       })
       .catch(() => {
         /* no-op */
       });
   }
 }, [postalCode]);
 const LocationPicker = () => {
   useMapEvents({
     click(e) {
       setLat(e.latlng.lat);
       setLng(e.latlng.lng);
     },
   });
   return null;
 };
 const onFilesChange = (e: ChangeEvent<HTMLInputElement>) => {
   if (e.target.files) {
     setFiles(prev => [...prev, ...Array.from(e.target.files)]);
   }
 };
 const handleDrop = (e: DragEvent<HTMLDivElement>) => {
   e.preventDefault();
   setDragActive(false);
   if (e.dataTransfer.files) {
     setFiles(prev => [...prev, ...Array.from(e.dataTransfer.files)]);
   }
 };
 const removeFile = (index: number) => {
   setFiles(prev => prev.filter((_, i) => i !== index));
 };
 const handleReset = () => {
   setPrefCode("");
   setPostalCode("");
   setAddress("");
   setFiles([]);
   setLat(35.68);
   setLng(139.76);
 };
 const goNext = () => {
   navigate("/estimate", {
     state: { lat, lng, prefCode, postalCode, files, address },
   });
 };
 return (
<div className={styles.container}>
<header>
<h1>建築・地価 見積もりシステム</h1>
</header>
<div className={styles.formGroup}>
<label>都道府県</label>
<select
         value={prefCode}
         onChange={e => setPrefCode(e.target.value)}
>
<option value="">選択してください</option>
<option value="01">北海道</option>
<option value="13">東京都</option>
<option value="27">大阪府</option>
         {/* 他の都道府県 */}
</select>
</div>
<div className={styles.formGroup}>
<label>郵便番号</label>
<input
         type="text"
         value={postalCode}
         onChange={e => setPostalCode(e.target.value.replace(/\D/g, ""))}
         placeholder="例: 1000001"
         maxLength={7}
       />
       {address && <small>住所自動設定： {address}</small>}
</div>
<div
       className={`${styles.dropZone} ${dragActive ? styles.active : ""}`}
       onDragOver={e => {
         e.preventDefault();
         setDragActive(true);
       }}
       onDragLeave={() => setDragActive(false)}
       onDrop={handleDrop}
>
<p>ここに写真や図面をドロップ、または選択</p>
<input
         type="file"
         multiple
         accept="image/*,.pdf"
         onChange={onFilesChange}
       />
</div>
<div className={styles.preview}>
       {files.map((file, i) => (
<div key={i} className={styles.previewItem}>
           {file.type.startsWith("image/") ? (
<img
               src={URL.createObjectURL(file)}
               alt={`preview-${i}`}
               width={100}
             />
           ) : (
<div className={styles.filePlaceholder}>
               📄 {file.name} ({(file.size / 1024).toFixed(1)} KB)
</div>
           )}
<button
             type="button"
             aria-label={`ファイル ${file.name} を削除`}
             onClick={() => removeFile(i)}
>
             削除
</button>
</div>
       ))}
</div>
<div className={styles.mapWrapper}>
<MapContainer
         center={[lat, lng]}
         zoom={13}
         style={{ height: 400 }}
>
<TileLayer
           url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
           attribution="© OpenStreetMap contributors"
         />
<LocationPicker />
<Marker position={[lat, lng]} />
</MapContainer>
</div>
<p>
       選択位置： 緯度 {lat.toFixed(5)} ／ 経度 {lng.toFixed(5)}
</p>
<div className={styles.buttons}>
<button
         type="button"
         onClick={handleReset}
>
         リセット
</button>
<button
         type="button"
         disabled={!canGoNext}
         onClick={goNext}
>
         見積に進む
</button>
</div>
</div>
 );
};
export default TopPage;