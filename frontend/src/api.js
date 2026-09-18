const TOKEN_KEY = "aicp_token";
const USER_KEY = "aicp_user";
const BACKEND_BASE_URL = (typeof import.meta !== "undefined" && import.meta.env && import.meta.env.VITE_API_URL) || "http://127.0.0.1:5000";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getUser() {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

export function setSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const token = getToken() || "demo-student-token";
  if (token) headers.Authorization = `Bearer ${token}`;
  const url = path.startsWith("http://") || path.startsWith("https://")
    ? path
    : `${BACKEND_BASE_URL}${path.startsWith("/") ? "" : "/"}${path}`;
  const res = await fetch(url, { ...options, headers });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || "Request failed");
  }
  return data;
}

export { BACKEND_BASE_URL };
