export function login(token, role) {
  localStorage.setItem("access_token", token);
  localStorage.setItem("role", role);
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("role");
}

export function getRole() {
  return localStorage.getItem("role");
}
