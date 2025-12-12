import axios, { AxiosError, type InternalAxiosRequestConfig, type AxiosInstance } from "axios";
import Cookies from "js-cookie";
import type { AuthTokens, ApiErrorResponse } from "./types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

// --- Cookie Keys ---
// Note: access_token and refresh_token are now httpOnly cookies set by backend
// We can't read them directly in JS - browser sends them automatically
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

// httpOnly cookie names (set by backend, readable only in server requests)
const HTTPONLY_ACCESS_TOKEN = "access_token";
const HTTPONLY_REFRESH_TOKEN = "refresh_token";

// --- Server-side helpers (for use in loaders) ---
// Note: httpOnly cookies are automatically sent by browser, but we can read them
// from the forwarded Cookie header in SSR loaders
export function getTokenFromServerRequest(request: Request): string | null {
  return getValueFromRequest(request, HTTPONLY_ACCESS_TOKEN);
}

export function getGuestCartIdFromServerRequest(request: Request): string | null {
  return getValueFromRequest(request, GUEST_CART_ID_KEY);
}

// --- API Factory: Creates per-request axios instance (SSR-safe) ---
export function createApi(request?: Request): AxiosInstance {
  const instance = axios.create({
    baseURL: API_URL,
    headers: { "Content-Type": "application/json" },
    withCredentials: true, // Important: send cookies with requests
  });

  instance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      // Server Side: Get token from request header (for SSR loaders)
      if (request && typeof window === "undefined") {
        const token = getTokenFromServerRequest(request);
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      }
      // Client Side: Browser automatically sends httpOnly cookies via withCredentials
      // No need to manually attach Authorization header
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
  withCredentials: true, // Important: send cookies with requests
});

// --- Token Management ---
// Tokens are httpOnly cookies set by backend - not accessible to JS
// These are now no-op functions kept for API compatibility
export function setTokens(_tokens: AuthTokens | null) {
  // No-op: Backend manages httpOnly cookies directly
  // We can't set or clear them from JS (security feature)
}

export function getTokens(): AuthTokens | null {
  // httpOnly tokens are not readable in JS - return null
  // Browser sends them automatically with withCredentials: true
  return null;
}

// Check if user is authenticated
// Since tokens are httpOnly, we can't read them directly
// Caller should check API response or use a store/context
export function isAuthenticated(): boolean {
  // Cannot determine from JS - caller should verify via API call
  // or maintain authentication state in context/store
  return false;
}

// --- Interceptors ---

// Request: No manual token attachment needed
// httpOnly cookies are sent automatically by browser via withCredentials: true
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => config,
  (error) => Promise.reject(error)
);

// Response: Handle Refresh Token
let isRefreshing = false;
let failedQueue: Array<{
  resolve: () => void;
  reject: (error: AxiosError) => void;
}> = [];

const processQueue = (error: AxiosError | null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve();
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

    // Skip if not 401 or already retried
    if (
      error.response?.status !== 401 ||
      originalRequest._retry ||
      originalRequest.url?.includes("/auth/token_refresh/") // Avoid loop
    ) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({
          resolve: () => {
            // Retry the request - browser will send new httpOnly cookie automatically
            resolve(api(originalRequest));
          },
          reject,
        });
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      // Call refresh endpoint - browser sends httpOnly refresh_token cookie automatically
      // Backend will set new httpOnly cookies in response
      await axios.post(
        `${API_URL}/auth/token_refresh/`,
        {},  // No body needed - refresh token is in httpOnly cookie
        { withCredentials: true }  // Important: send/receive cookies
      );
      
      processQueue(null);

      // Retry original request - browser sends new httpOnly cookie automatically
      return api(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError as AxiosError);
      
      // Redirect to login if not already there
      if (typeof window !== "undefined" && !window.location.pathname.includes("/auth/login")) {
        window.location.href = "/auth/login";
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