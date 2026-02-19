// frontend/src/api/auth.js

// Save token to localStorage
export function setToken(token) {
  localStorage.setItem("access_token", token);
}

// Get token from localStorage
export function getToken() {
  return localStorage.getItem("access_token");
}

// Remove token (logout)
export function clearToken() {
  localStorage.removeItem("access_token");
}
