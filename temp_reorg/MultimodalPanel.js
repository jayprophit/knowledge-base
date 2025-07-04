import React, { useState } from 'react';

export default function MultimodalPanel({ onAnalyze }) {
  const [file, setFile] = useState(null);
  const [type, setType] = useState('image');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setResult(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', type);
      const res = await onAnalyze(formData);
      setResult(res.result);
    } catch (err) {
      setResult('Error analyzing file.');
    }
    setLoading(false);
  };

  return (
    <div className="multimodal-panel">
      <h2>Multimodal Analysis (Image/Audio)</h2>
      <form onSubmit={handleSubmit} className="multimodal-form">
        <input
          type="file"
          accept={type === 'image' ? 'image/*' : 'audio/*'}
          onChange={e => setFile(e.target.files[0])}
          className="multimodal-file-input"
        />
        <select value={type} onChange={e => setType(e.target.value)} className="multimodal-type-select">
          <option value="image">Image</option>
          <option value="audio">Audio</option>
        </select>
        <button type="submit" disabled={!file || loading} className="multimodal-analyze-btn">
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </form>
      {result && (
        <div className="multimodal-result">{result}</div>
      )}
    </div>
  );
}
