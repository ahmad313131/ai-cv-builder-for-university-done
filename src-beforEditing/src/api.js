// src/api.js
// ✅ جاهز للمحلي والديبلوي: غيّر REACT_APP_API_URL عند النشر
export const API_BASE =
  process.env.REACT_APP_API_URL || "http://localhost:8000";

export const ENDPOINTS = {
  fast: `${API_BASE}/api/analyze_cv`,
  llm: `${API_BASE}/api/llm_analyze_cv`,
  upload: `${API_BASE}/api/upload_photo`,
  save: `${API_BASE}/api/cv`,
  pdf: `${API_BASE}/api/generate_cv`,
  // 🔐 Auth
  register: `${API_BASE}/api/auth/register`,
  login: `${API_BASE}/api/auth/login`,
  me: `${API_BASE}/api/auth/me`,
  myCvs: `${API_BASE}/api/cvs`,
};

/* -------------------- Helpers: Token & Requests -------------------- */
const TOKEN_KEY = "token";

export function setToken(t) {
  if (t) localStorage.setItem(TOKEN_KEY, t);
  else localStorage.removeItem(TOKEN_KEY);
}
export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || null;
}
export function logout() {
  setToken(null);
}

export function authHeader() {
  const t = getToken();
  return t ? { Authorization: `Bearer ${t}` } : {};
}

async function jsonOrThrow(res) {
  const txt = await res.text();
  let data = null;
  try {
    data = txt ? JSON.parse(txt) : null;
  } catch {}
  if (!res.ok) {
    const msg =
      data?.detail || data?.message || `Request failed (${res.status})`;
    throw new Error(msg);
  }
  return data;
}

// Wrapper يحقن الهيدرز ويعالج 401/أخطاء الشبكة
async function request(
  url,
  { method = "GET", headers = {}, body, signal } = {}
) {
  const baseHeaders = { ...authHeader(), ...headers };
  let res;
  try {
    res = await fetch(url, { method, headers: baseHeaders, body, signal });
  } catch (err) {
    console.error("Network/CORS error:", err);
    throw new Error("Network error (CORS or server down)");
  }

  if (res.status === 401) {
    // انتهت صلاحية التوكن أو غير صالح
    logout();
    const next = encodeURIComponent(
      window.location.pathname + window.location.search
    );
    // لو عم نستدعي من /login نفسه، ما نعمل لوب
    if (!window.location.pathname.startsWith("/login")) {
      window.location.assign(`/login?next=${next}`);
    }
    throw new Error("Unauthorized");
  }

  return res;
}

/* -------------------- Public API: Upload/Analyze/Save/PDF -------------------- */

export async function uploadPhoto(file) {
  const data = new FormData();
  data.append("file", file);
  const res = await request(ENDPOINTS.upload, {
    method: "POST",
    // لا تضف Content-Type مع FormData
    body: data,
  });
  return jsonOrThrow(res); // { path: "/uploads/xxx.jpg" }
}

export async function saveCV(formData) {
  // حماية إضافية: منع الحفظ بدون توكن
  if (!getToken()) throw new Error("Please sign in to save your CV");
  const res = await request(ENDPOINTS.save, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData),
  });
  return jsonOrThrow(res);
}

export async function analyzeCV(formData) {
  const res = await request(ENDPOINTS.fast, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData),
  });
  return jsonOrThrow(res);
}

export async function analyzeCVLLM(formData) {
  const res = await request(ENDPOINTS.llm, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData),
  });
  return jsonOrThrow(res);
}

export async function generateCV(formData) {
  const res = await request(ENDPOINTS.pdf, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData),
  });
  if (!res.ok) throw new Error(`Download failed (${res.status})`);
  return res.blob();
}

export async function downloadCV(formData, filename = "cv.pdf", signal) {
  const res = await request(ENDPOINTS.pdf, {
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

/* -------------------- Auth API: register / login / me -------------------- */

export async function register(email, password, username) {
  const res = await request(ENDPOINTS.register, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, username }),
  });
  return jsonOrThrow(res); // { id, email , username}
}

export async function login(email, password) {
  // OAuth2 form fields: username + password
  const body = new URLSearchParams();
  body.append("username", email);
  body.append("password", password);

  const res = await request(ENDPOINTS.login, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  const data = await jsonOrThrow(res); // { access_token, token_type }
  setToken(data?.access_token);
  return data;
}

export async function me() {
  const res = await request(ENDPOINTS.me, { method: "GET" });
  return jsonOrThrow(res); // { id, email }
}

/* -------------------- User CVs -------------------- */

export async function listCVs() {
  const res = await request(ENDPOINTS.myCvs, { method: "GET" });
  return jsonOrThrow(res); // [{id, name, email, created_at, note}, ...]
}

export async function getCV(id) {
  const res = await request(`${ENDPOINTS.save}/${id}/raw`, { method: "GET" });
  return jsonOrThrow(res); // يرجّع كل الحقول المخزنة
}
