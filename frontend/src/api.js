// API utility for the Knowledge Base Assistant with environment-aware configuration

// Determine the API base URL based on environment
const getApiBaseUrl = () => {
  // Check if we're in production (deployed site)
  if (process.env.NODE_ENV === 'production') {
    // In production, use relative URLs which will be proxied by Netlify
    // This assumes proper Netlify redirect setup in netlify.toml
    return '/api';
  } else if (process.env.REACT_APP_API_URL) {
    // Use environment variable if specified
    return process.env.REACT_APP_API_URL;
  } else {
    // Default to localhost for development
    return 'http://localhost:8000';
  }
};

const API_BASE = getApiBaseUrl();

// For debugging
console.log(`Using API endpoint: ${API_BASE}`);


export async function fetchCategories() {
  const res = await fetch(`${API_BASE}/categories`);
  if (!res.ok) throw new Error('Failed to fetch categories');
  return res.json();
}

export async function fetchCategoryFiles(categoryId) {
  const res = await fetch(`${API_BASE}/category/${categoryId}/files`);
  if (!res.ok) throw new Error('Failed to fetch files');
  return res.json();
}

export async function fetchFileContent(path) {
  const res = await fetch(`${API_BASE}/file?path=${encodeURIComponent(path)}`);
  if (!res.ok) throw new Error('Failed to fetch file content');
  return res.json();
}

export async function searchKnowledgeBase(query) {
  const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error('Failed to search knowledge base');
  return res.json();
}

export async function generateCode({ prompt, language }) {
  const res = await fetch(`${API_BASE}/generate_code`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, language })
  });
  if (!res.ok) throw new Error('Failed to generate code');
  return res.json();
}

export async function analyzeMultimodal(formData) {
  const res = await fetch(`${API_BASE}/analyze_multimodal`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) throw new Error('Failed to analyze file');
  return res.json();
}
