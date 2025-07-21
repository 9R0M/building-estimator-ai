//estimate-app\frontend\src\components\EstimateEditor.tsx
import React, { useState } from 'react';
type Row = {
 id: number;
 category: string;
 item: string;
 quantity: number;
 unit: string;
 unitPrice: number;
 remarks: string;
};
type EditableField = keyof Omit<Row, 'id'>;
const initialRows: Row[] = [
 { id: 1, category: '仮設工事', item: '', quantity: 1, unit: '式', unitPrice: 10000, remarks: '' }
];
const EstimateEditor: React.FC = () => {
 const [rows, setRows] = useState<Row[]>(initialRows);
 const handleChange = (index: number, field: EditableField, value: string | number) => {
   const updated = [...rows];
   updated[index] = { ...updated[index], [field]: value };
   setRows(updated);
 };
 return (
<table>
<thead>
<tr>
<th>分類</th>
<th>小項目</th>
<th>数量</th>
<th>単位</th>
<th>単価</th>
<th>金額</th>
<th>備考</th>
</tr>
</thead>
<tbody>
       {rows.map((row, idx) => (
<tr key={row.id}>
<td>
<input
       value={row.category}
       onChange={(e) => handleChange(idx, 'category', e.target.value)}
             />
</td>
<td>
<input
        value={row.item}
        onChange={(e) => handleChange(idx, 'item', e.target.value)}
             />
</td>
<td>
<input
        type="number"
        value={row.quantity}
        onChange={(e) => handleChange(idx, 'quantity', Number(e.target.value))}
             />
</td>
<td>
<input
        value={row.unit}
        onChange={(e) => handleChange(idx, 'unit', e.target.value)}
             />
</td>
<td>
<input
        type="number"
        value={row.unitPrice}
        onChange={(e) => handleChange(idx, 'unitPrice', Number(e.target.value))}
             />
</td>
<td>{row.quantity * row.unitPrice} 円</td>
<td>
<input
        value={row.remarks}
        onChange={(e) => handleChange(idx, 'remarks', e.target.value)}/>
</td>
</tr>
       ))}
</tbody>
</table>
 );
};
export default EstimateEditor;