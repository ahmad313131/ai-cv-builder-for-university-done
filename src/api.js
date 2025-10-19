// src/api.js
export const API_BASE = "http://localhost:8000";

export const ENDPOINTS = {
  fast: `${API_BASE}/api/analyze_cv`,
  llm: `${API_BASE}/api/llm_analyze_cv`,
  upload: `${API_BASE}/api/upload_photo`,
  save: `${API_BASE}/api/cv`,
  pdf: `${API_BASE}/api/generate_cv`,
};

async function jsonOrThrow(res) {
  const data = await res.json().catch(() => null);
  if (!res.ok)
    throw new Error(data?.detail || `Request failed (${res.status})`);
  return data;
}

export async function uploadPhoto(file) {
  const data = new FormData();
  data.append("file", file);
  const res = await fetch(ENDPOINTS.upload, { method: "POST", body: data });
  return jsonOrThrow(res); // { path: "/uploads/xxx.jpg" }
}

export async function saveCV(formData) {
  const res = await fetch(ENDPOINTS.save, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData),
  });
  return jsonOrThrow(res);
}

export async function analyzeCV(formData) {
  const res = await fetch(ENDPOINTS.fast, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData),
  });
  return jsonOrThrow(res);
}

// جديد: تحليل عبر LLM (llm_analyze_cv)
export async function analyzeCVLLM(formData) {
  const res = await fetch(ENDPOINTS.llm, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData),
  });
  return jsonOrThrow(res);
}

export async function generateCV(formData) {
  const res = await fetch(ENDPOINTS.pdf, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData),
  });
  if (!res.ok) throw new Error(`Download failed (${res.status})`);
  return res.blob();
}
// src/api.js (أضِف تحت generateCV)
export async function downloadCV(formData, filename = "cv.pdf", signal) {
  const res = await fetch(ENDPOINTS.pdf, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData),
    signal,
  });
  if (!res.ok)
    throw new Error(await res.text().catch(() => `HTTP ${res.status}`));

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
