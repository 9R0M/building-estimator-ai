// src/pages/TopPage.tsx
import React, { useState, type DragEvent, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { MapContainer, TileLayer, Marker, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import styles from "../styles/TopPage.module.css";
import axios from "axios";
const TopPage: React.FC = () => {
  const [lat, setLat] = useState(35.68);
  const [lng, setLng] = useState(139.76);
  const [prefCode, setPrefCode] = useState("");
  const [postalCode, setPostalCode] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const LocationPicker = () => {
    useMapEvents({
      click(e) {
        setLat(e.latlng.lat);
        setLng(e.latlng.lng);
      },
    });
    return null;
  };
  const onFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const arr = Array.from(e.target.files);
      const valid = arr.filter(f => f.type.startsWith("image/"));
      if (valid.length !== arr.length) {
        setError("画像ファイルのみ許可されています");
      }
      setFiles(prev => [...prev, ...valid]);
    }
  };
  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragActive(false);
    const arr = Array.from(e.dataTransfer.files);
    const valid = arr.filter(f => f.type.startsWith("image/"));
    if (valid.length !== arr.length) {
      setError("画像ファイルのみ許可されています");
    }
    setFiles(prev => [...prev, ...valid]);
  };
  const removeFile = (i: number) => setFiles(prev => prev.filter((_, idx) => idx !== i));
  const queryPostal = async () => {
    if (!postalCode.match(/^\d{7}$/)) {
      setError("郵便番号は7桁で入力してください");
      return;
    }
    try {
      const res = await axios.get(`https://api.zipaddress.net/?zipcode=${postalCode}`);
      if (res.data && res.data.code === 200) {
        const { lat: pLat, lng: pLng } = res.data;
        setLat(parseFloat(pLat));
        setLng(parseFloat(pLng));
        setError("");
      } else {
        setError("住所情報が取得できませんでした");
      }
    } catch {
      setError("郵便番号検索に失敗しました");
    }
  };
  const goNext = () => {
    if (!prefCode) {
      setError("都道府県を選んでください");
      return;
    }
    navigate("/estimate", {
      state: { lat, lng, prefCode, postalCode, files },
    });
  };
  return (
    <div className={styles.container}>
      <h1>建築・地価 見積もりシステム</h1>
      {error && <p className={styles.error}>{error}</p>}
      <div className={styles.formGroup}>
        <label>都道府県</label>
        <select value={prefCode} onChange={e => setPrefCode(e.target.value)}>
          <option value="">選択してください</option>
          <option value="01">北海道</option>
          <option value="13">東京都</option>
          <option value="27">大阪府</option>
        </select>
      </div>
      <div className={styles.formGroup}>
        <label>郵便番号</label>
        <div style={{ display: "flex", gap: 8 }}>
          <input
            type="text"
            value={postalCode}
            onChange={e => setPostalCode(e.target.value)}
            placeholder="1000001"
          />
          <button type="button" onClick={queryPostal}>住所検索</button>
        </div>
      </div>
      <div
        className={`${styles.dropZone} ${dragActive ? styles.active : ""}`}
        onDragOver={e => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        tabIndex={0}
        onKeyDown={e => { if (e.key === "Enter" || e.key === " ") e.currentTarget.querySelector('input')?.click(); }}
      >
        <p>ここに画像をドロップ<br />またはクリックして選択</p>
        <input className={styles.fileInput} type="file" multiple accept="image/*" onChange={onFilesChange} aria-label="画像ファイル選択" />
      </div>
      <div className={styles.preview}>
        {files.map((f, i) => (
          <div key={i} className={styles.previewItem}>
            <img src={URL.createObjectURL(f)} alt={`プレビュー画像${i}`} />
            <div className={styles.fileInfo}>
              <span>{f.name}</span>
              <button type="button" onClick={() => removeFile(i)} aria-label={`画像${i}を削除`}>✕</button>
            </div>
          </div>
        ))}
      </div>
      <div className={styles.mapWrapper}>
        <MapContainer center={[lat, lng]} zoom={13} style={{ height: 400 }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="© OpenStreetMap contributors" />
          <LocationPicker />
          <Marker position={[lat, lng]} />
        </MapContainer>
      </div>
      <p>選択された位置： 緯度 {lat.toFixed(5)} ／ 経度 {lng.toFixed(5)}</p>
      <button type="button" className={styles.nextButton} onClick={goNext}>見積に進む</button>
    </div>
  );
};
export default TopPage;