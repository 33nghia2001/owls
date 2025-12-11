import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import type { AuthTokens, ApiError } from "./types";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1";

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

// Token management
let accessToken: string | null = null;
let refreshToken: string | null = null;

export function setTokens(tokens: AuthTokens | null) {
  if (tokens) {
    accessToken = tokens.access;
    refreshToken = tokens.refresh;
    if (typeof window !== "undefined") {
      localStorage.setItem("accessToken", tokens.access);
      localStorage.setItem("refreshToken", tokens.refresh);
    }
  } else {
    accessToken = null;
    refreshToken = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
    }
  }
}

export function getTokens(): AuthTokens | null {
  if (typeof window === "undefined") return null;
  
  if (!accessToken) {
    accessToken = localStorage.getItem("accessToken");
    refreshToken = localStorage.getItem("refreshToken");
  }
  
  if (accessToken && refreshToken) {
    return { access: accessToken, refresh: refreshToken };
  }
  return null;
}

// Request interceptor - add auth header
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const tokens = getTokens();
    if (tokens?.access) {
      config.headers.Authorization = `Bearer ${tokens.access}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle token refresh
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

    // Skip if no refresh token or already retried
    if (
      error.response?.status !== 401 ||
      originalRequest._retry ||
      !refreshToken
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
      const response = await axios.post<AuthTokens>(
        `${API_URL}/auth/token/refresh/`,
        { refresh: refreshToken }
      );

      const newTokens = response.data;
      setTokens(newTokens);
      processQueue(null, newTokens.access);

      originalRequest.headers.Authorization = `Bearer ${newTokens.access}`;
      return api(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError as AxiosError, null);
      setTokens(null);
      
      // Redirect to login
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

// Guest cart ID management
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
