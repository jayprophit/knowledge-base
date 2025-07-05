import React, { useState } from 'react';

export default function CodeGenPanel({ onGenerate }) {
  const [prompt, setPrompt] = useState('');
  const [language, setLanguage] = useState('python');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const res = await onGenerate({ prompt, language });
      setResult(res.code);
    } catch (err) {
      setResult('Error generating code.');
    }
    setLoading(false);
  };

  return (
    <div className="codegen-panel">
      <h2>AI Code Generation</h2>
      <form onSubmit={handleSubmit} className="codegen-form">
        <input
          type="text"
          placeholder="Describe what you want to generate..."
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          className="codegen-input"
        />
        <select value={language} onChange={e => setLanguage(e.target.value)} className="codegen-select">
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
          <option value="typescript">TypeScript</option>
          <option value="cpp">C++</option>
          <option value="java">Java</option>
          <option value="go">Go</option>
        </select>
        <button type="submit" disabled={!prompt || loading} className="codegen-generate-btn">
          {loading ? 'Generating...' : 'Generate Code'}
        </button>
      </form>
      {result && (
        <pre className="codegen-result"><code>{result}</code></pre>
      )}
    </div>
  );
}
