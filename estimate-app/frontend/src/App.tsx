import { useState } from 'react';
import axios from 'axios';
import styles from './styles/App.module.css';

type LineItem = {
  description: string;
  quantity: number;
  unitPrice: number;
};

type EstimateState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; estimate: number }
  | { status: 'error'; message: string };

export default function App() {
  const [structure, setStructure] = useState("RC");
  const [floors, setFloors] = useState(5);
  const [area, setArea] = useState(1000);
  const [usage, setUsage] = useState("オフィス");
  const [items, setItems] = useState<LineItem[]>([
    { description: '', quantity: 1, unitPrice: 0 }
  ]);
  const [estimateState, setEstimateState] = useState<EstimateState>({ status: 'idle' });

  const handleItemChange = (index: number, field: keyof LineItem, value: string | number) => {
    const newItems = [...items];
    newItems[index][field] = typeof value === 'string' && field !== 'description' ? Number(value) : value;
    setItems(newItems);
  };

  const handleAddItem = () => {
    setItems([...items, { description: '', quantity: 1, unitPrice: 0 }]);
  };

  const handleRemoveItem = (index: number) => {
    const newItems = items.filter((_, i) => i !== index);
    setItems(newItems);
  };

  const getTotal = () =>
    items.reduce((sum, item) => sum + item.quantity * item.unitPrice, 0);

  const handleEstimate = async () => {
    setEstimateState({ status: 'loading' });
    try {
      const res = await axios.post("http://localhost:8000/estimate", {
        structure, floors, area, usage, items
      });
      setEstimateState({ status: 'success', estimate: res.data.estimate });
    } catch {
      setEstimateState({ status: 'error', message: '見積もりに失敗しました。' });
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>建物見積もりAI</h1>

      <div className={styles.formGroup}>
        <label>構造</label>
        <select value={structure} onChange={e => setStructure(e.target.value)}>
          {["RC", "SRC", "S"].map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      <div className={styles.formGroup}>
        <label>階数</label>
        <input type="number" value={floors} onChange={e => setFloors(Number(e.target.value))} />
      </div>

      <div className={styles.formGroup}>
        <label>延床面積（㎡）</label>
        <input type="number" value={area} onChange={e => setArea(Number(e.target.value))} />
      </div>

      <div className={styles.formGroup}>
        <label>用途</label>
        <select value={usage} onChange={e => setUsage(e.target.value)}>
          {["オフィス", "住宅", "商業施設", "工場", "ビル", "学校"].map(u => <option key={u} value={u}>{u}</option>)}
        </select>
      </div>

      <h2>明細項目</h2>
      {items.map((item, index) => (
        <div key={index} className={styles.itemRow}>
          <input type="text" placeholder="内容" value={item.description}
            onChange={e => handleItemChange(index, 'description', e.target.value)} />
          <input type="number" placeholder="数量" value={item.quantity}
            onChange={e => handleItemChange(index, 'quantity', e.target.value)} />
          <input type="number" placeholder="単価" value={item.unitPrice}
            onChange={e => handleItemChange(index, 'unitPrice', e.target.value)} />
          <span>{(item.quantity * item.unitPrice).toLocaleString()} 円</span>
          <button onClick={() => handleRemoveItem(index)}>削除</button>
        </div>
      ))}
      <button onClick={handleAddItem}>＋ 行を追加</button>

      <div>
        合計金額：<strong>{getTotal().toLocaleString()} 円</strong>
      </div>

      <button className={styles.button} onClick={handleEstimate}>見積もりを実行</button>

      <div className={styles.resultBox}>
        {estimateState.status === 'loading' && <p>計算中...</p>}
        {estimateState.status === 'success' && (
          <p className={styles.success}>見積金額：<strong>{estimateState.estimate.toLocaleString()} 円</strong></p>
        )}
        {estimateState.status === 'error' && (
          <p className={styles.error}>{estimateState.message}</p>
        )}
      </div>
    </div>
  );
}
