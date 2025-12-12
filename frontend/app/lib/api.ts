import axios, { AxiosError, type InternalAxiosRequestConfig, type AxiosInstance } from "axios";
import Cookies from "js-cookie";
import type { AuthTokens, ApiErrorResponse } from "./types";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1";

// --- Cookie Keys ---
const ACCESS_TOKEN_KEY = "accessToken";
const REFRESH_TOKEN_KEY = "refreshToken";
const GUEST_CART_ID_KEY = "guestCartId";

// --- Helper: Parse token from Server Request Cookie Header ---
function parseCookieHeader(cookieHeader: string): Record<string, string> {
  return cookieHeader.split(";").reduce((acc, cookie) => {
    const [name, value] = cookie.trim().split("=");
    if (name && value) acc[name] = decodeURIComponent(value);
    return acc;
  }, {} as Record<string, string>);
}

function getValueFromRequest(request: Request, key: string): string | null {
  const cookieHeader = request.headers.get("Cookie");
  if (!cookieHeader) return null;
  const cookies = parseCookieHeader(cookieHeader);
  return cookies[key] || null;
}

// --- Server-side helpers (for use in loaders) ---
export function getTokenFromServerRequest(request: Request): string | null {
  return getValueFromRequest(request, ACCESS_TOKEN_KEY);
}

export function getGuestCartIdFromServerRequest(request: Request): string | null {
  return getValueFromRequest(request, GUEST_CART_ID_KEY);
}

// --- API Factory: Creates per-request axios instance (SSR-safe) ---
export function createApi(request?: Request): AxiosInstance {
  const instance = axios.create({
    baseURL: API_URL,
    headers: { "Content-Type": "application/json" },
    withCredentials: true,
  });

  instance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      let token: string | null = null;

      // Server Side: Get token from request header
      if (request && typeof window === "undefined") {
        token = getValueFromRequest(request, ACCESS_TOKEN_KEY);
      }
      // Client Side: Get token from cookie
      else if (typeof window !== "undefined") {
        token = Cookies.get(ACCESS_TOKEN_KEY) || null;
      }

      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  return instance;
}

// --- Default API instance (for client-side hooks like React Query) ---
export const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
});

// --- Token Management (Cookie-based) ---
export function setTokens(tokens: AuthTokens | null) {
  if (typeof window === "undefined") return;

  if (tokens) {
    const isSecure = window.location.protocol === "https:";
    Cookies.set(ACCESS_TOKEN_KEY, tokens.access, { secure: isSecure, sameSite: "Lax", expires: 1 });
    Cookies.set(REFRESH_TOKEN_KEY, tokens.refresh, { secure: isSecure, sameSite: "Lax", expires: 7 });
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
  async (error: AxiosError<ApiErrorResponse>) => {
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

// Guest Cart Management (Cookie-based for SSR compatibility)
export function getGuestCartId(): string | null {
  if (typeof window === "undefined") return null;
  return Cookies.get(GUEST_CART_ID_KEY) || null;
}

export function setGuestCartId(id: string | null) {
  if (typeof window === "undefined") return;
  
  if (id) {
    Cookies.set(GUEST_CART_ID_KEY, id, { 
      secure: window.location.protocol === "https:",
      sameSite: "Lax",
      expires: 30 // 30 days
    });
  } else {
    Cookies.remove(GUEST_CART_ID_KEY);
  }
}

export default api;