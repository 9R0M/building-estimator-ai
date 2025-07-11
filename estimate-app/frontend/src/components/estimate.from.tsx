import React, { useState, ChangeEvent } from 'react'
import axios from 'axios'

type ResultData = {
  structure: string
  floors: number
  area: number
  raw_text?: string
}

const EstimateForm: React.FC = () => {
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<ResultData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0])
    }
  }

  const handleSubmit = async () => {
    if (!file) return
    setLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await axios.post('http://localhost:8000/extract-info/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setResult(res.data)
    } catch (err) {
      setError("OCR処理に失敗しました")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '2rem' }}>
      <h2>建物図面OCRアップロード</h2>
      <input type="file" accept="image/*" onChange={handleFileChange} />
      <button onClick={handleSubmit} disabled={loading || !file}>
        {loading ? '送信中...' : '見積もり開始'}
      </button>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {result && (
        <div style={{ marginTop: '1rem' }}>
          <h3>見積もり結果</h3>
          <p><strong>構造:</strong> {result.structure}</p>
          <p><strong>階数:</strong> {result.floors}</p>
          <p><strong>面積:</strong> {result.area}㎡</p>
        </div>
      )}
    </div>
  )
}

export default EstimateForm