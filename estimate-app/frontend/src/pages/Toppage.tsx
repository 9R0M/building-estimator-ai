import React, { useState, type DragEvent } from "react";
import { useNavigate } from "react-router-dom";
import { MapContainer, TileLayer, Marker, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import styles from "../styles/TopPage.module.css";
import axios from "axios";
 
// Leafletのデフォルトアイコンの設定を修正
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});
const TopPage: React.FC = () => {
  const [lat, setLat] = useState<number>(36.2048); // 日本の中央付近（長野県）
  const [lng, setLng] = useState<number>(138.2529);
  const [prefCode, setPrefCode] = useState("");
  const [postalCode, setPostalCode] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState("");
  const [landPrice, setLandPrice] = useState<number | null>(null);
  const [landPriceLoading, setLandPriceLoading] = useState(false);
  const navigate = useNavigate();
  const LocationPicker = () => {
    useMapEvents({
      click(e: L.LeafletMouseEvent) {
        const newLat = e.latlng.lat;
        const newLng = e.latlng.lng;
        setLat(newLat);
        setLng(newLng);
        // 都道府県が選択されている場合は地価も自動取得
        if (prefCode) {
          fetchLandPrice(newLat, newLng);
        }
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
        // 位置が更新されたら地価情報も取得
        await fetchLandPrice(parseFloat(pLat), parseFloat(pLng));
      } else {
        setError("住所情報が取得できませんでした");
      }
    } catch {
      setError("郵便番号検索に失敗しました");
    }
  };
 
  // 地価情報を取得する関数
  const fetchLandPrice = async (latitude: number, longitude: number) => {
    if (!prefCode) {
      // 都道府県未選択時は地価取得をスキップ（エラーは出さない）
      return;
    }
   
    setLandPriceLoading(true);
    try {
      // バックエンドAPIに地価情報を問い合わせ
      const response = await axios.post('/api/land-price', {
        lat: latitude,
        lng: longitude,
        pref_code: prefCode,
        postal_code: postalCode
      });
     
      if (response.data && response.data.land_price) {
        setLandPrice(response.data.land_price);
        setError("");
      } else {
        setError("地価情報を取得できませんでした");
      }
    } catch (err) {
      console.error('地価取得エラー:', err);
      setError("地価情報の取得に失敗しました");
    } finally {
      setLandPriceLoading(false);
    }
  };
 
  // 地価情報を手動で取得
  const getLandPrice = async () => {
    await fetchLandPrice(lat, lng);
  };
  const goNext = () => {
    navigate("/estimate", {
      state: { lat, lng, prefCode, postalCode, files, landPrice },
    });
  };
 
  // 都道府県変更時の処理
  const handlePrefCodeChange = async (newPrefCode: string) => {
    setPrefCode(newPrefCode);
    // 都道府県が選択され、位置情報がある場合は地価を自動取得
    if (newPrefCode && lat && lng) {
      await fetchLandPrice(lat, lng);
    }
  };
  return (
    <div className={styles.container}>
      <h1>建築・地価 見積もりシステム</h1>
      {error && <p className={styles.error}>{error}</p>}
      <div className={styles.formGroup}>
        <label>都道府県</label>
        <select value={prefCode} onChange={e => handlePrefCodeChange(e.target.value)}>
          <option value="">選択してください</option>
          <option value="01">北海道</option>
          <option value="02">青森県</option>
          <option value="03">岩手県</option>
          <option value="04">宮城県</option>
          <option value="05">秋田県</option>
          <option value="06">山形県</option>
          <option value="07">福島県</option>
          <option value="08">茨城県</option>
          <option value="09">栃木県</option>
          <option value="10">群馬県</option>
          <option value="11">埼玉県</option>
          <option value="12">千葉県</option>
          <option value="13">東京都</option>
          <option value="14">神奈川県</option>
          <option value="15">新潟県</option>
          <option value="16">富山県</option>
          <option value="17">石川県</option>
          <option value="18">福井県</option>
          <option value="19">山梨県</option>
          <option value="20">長野県</option>
          <option value="21">岐阜県</option>
          <option value="22">静岡県</option>
          <option value="23">愛知県</option>
          <option value="24">三重県</option>
          <option value="25">滋賀県</option>
          <option value="26">京都府</option>
          <option value="27">大阪府</option>
          <option value="28">兵庫県</option>
          <option value="29">奈良県</option>
          <option value="30">和歌山県</option>
          <option value="31">鳥取県</option>
          <option value="32">島根県</option>
          <option value="33">岡山県</option>
          <option value="34">広島県</option>
          <option value="35">山口県</option>
          <option value="36">徳島県</option>
          <option value="37">香川県</option>
          <option value="38">愛媛県</option>
          <option value="39">高知県</option>
          <option value="40">福岡県</option>
          <option value="41">佐賀県</option>
          <option value="42">長崎県</option>
          <option value="43">熊本県</option>
          <option value="44">大分県</option>
          <option value="45">宮崎県</option>
          <option value="46">鹿児島県</option>
          <option value="47">沖縄県</option>
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
     
      {/* 地価情報セクション */}
      <div className={styles.formGroup}>
        <label>地価情報</label>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <button
            type="button"
            onClick={getLandPrice}
            disabled={!prefCode || landPriceLoading}
          >
            {landPriceLoading ? "取得中..." : "地価取得"}
          </button>
          {landPrice && (
            <span className={styles.landPriceDisplay}>
              {landPrice.toLocaleString()} 円/㎡
            </span>
          )}
        </div>
        {landPrice && (
          <p className={styles.landPriceNote}>
            ※ 基準地価・公示地価を基にした推定値です
          </p>
        )}
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
        <MapContainer center={[lat, lng]} zoom={6} style={{ height: 400 }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"
          />
          <LocationPicker />
          {(lat !== 0 && lng !== 0) && <Marker position={[lat, lng]} />}
        </MapContainer>
      </div>
      <p>選択された位置： 緯度 {lat.toFixed(5)} ／ 経度 {lng.toFixed(5)}</p>
      <button type="button" className={styles.nextButton} onClick={goNext}>見積に進む</button>
    </div>
  );
};
export default TopPage;