import axios from "axios";

const api = axios.create({
  baseURL: "https://trade-finance-blockchain-explorer.onrender.com" || "http://127.0.0.1:8000" ,
  // baseURL: "https://trade-finance-blockchain-explorer.onrender.com" || "http://127.0.0.1:8000" ,
  withCredentials: true,
});

// 🔐 Auto-attach JWT token to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("accessToken");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;

