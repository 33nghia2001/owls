import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import Cookies from "js-cookie";
import type { AuthTokens, ApiError } from "./types";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1";

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

// --- Token Management (Cookie-based) ---
const ACCESS_TOKEN_KEY = "accessToken";
const REFRESH_TOKEN_KEY = "refreshToken";

export function setTokens(tokens: AuthTokens | null) {
  if (tokens) {
    // Lưu token vào cookie (Client side)
    // Secure: true nếu chạy HTTPS, SameSite: Strict để chống CSRF
    Cookies.set(ACCESS_TOKEN_KEY, tokens.access, { secure: window.location.protocol === 'https:', sameSite: 'Strict' });
    Cookies.set(REFRESH_TOKEN_KEY, tokens.refresh, { secure: window.location.protocol === 'https:', sameSite: 'Strict' });
  } else {
    Cookies.remove(ACCESS_TOKEN_KEY);
    Cookies.remove(REFRESH_TOKEN_KEY);
  }
}

export function getTokens(): AuthTokens | null {
  if (typeof window === "undefined") return null;
  
  const access = Cookies.get(ACCESS_TOKEN_KEY);
  const refresh = Cookies.get(REFRESH_TOKEN_KEY);
  
  if (access && refresh) {
    return { access, refresh };
  }
  return null;
}

// --- Interceptors ---

// Request: Attach Token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Chỉ chạy ở Client-side. Server-side cần cơ chế truyền header riêng (nếu dùng Loader)
    if (typeof window !== "undefined") {
      const tokens = getTokens();
      if (tokens?.access) {
        config.headers.Authorization = `Bearer ${tokens.access}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response: Handle Refresh Token
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: AxiosError) => void;
}> = [];

const processQueue = (error: AxiosError | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else if (token) {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    // Bỏ qua nếu lỗi không phải 401 hoặc đã retry rồi
    if (
      error.response?.status !== 401 ||
      originalRequest._retry ||
      originalRequest.url?.includes("/auth/token/refresh/") // Tránh loop nếu API refresh lỗi
    ) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({
          resolve: (token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            resolve(api(originalRequest));
          },
          reject,
        });
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      const tokens = getTokens();
      if (!tokens?.refresh) throw new Error("No refresh token");

      const response = await axios.post<AuthTokens>(
        `${API_URL}/auth/token/refresh/`,
        { refresh: tokens.refresh }
      );

      const newTokens = response.data;
      setTokens(newTokens);
      
      api.defaults.headers.common.Authorization = `Bearer ${newTokens.access}`;
      processQueue(null, newTokens.access);

      originalRequest.headers.Authorization = `Bearer ${newTokens.access}`;
      return api(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError as AxiosError, null);
      setTokens(null);
      
      if (typeof window !== "undefined" && !window.location.pathname.includes("/login")) {
        window.location.href = "/login";
      }
      
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

// Guest Cart Management
export function getGuestCartId(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("guestCartId");
}

export function setGuestCartId(id: string | null) {
  if (typeof window === "undefined") return;
  if (id) {
    localStorage.setItem("guestCartId", id);
  } else {
    localStorage.removeItem("guestCartId");
  }
}

export default api;