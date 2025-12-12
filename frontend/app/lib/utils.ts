import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number, currency: string = "VND"): string {
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat("vi-VN", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(new Date(date));
}

export function formatDateTime(date: string | Date): string {
  return new Intl.DateTimeFormat("vi-VN", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(date));
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str;
  return str.slice(0, length) + "...";
}

export function slugify(str: string): string {
  return str
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[đĐ]/g, "d")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}

/**
 * Safely parse price from various formats:
 * - Money object: { amount: string, currency: string }
 * - String: "100000.00" (from djmoney)
 * - Number: 100000
 * - null/undefined: returns 0
 */
export function parsePrice(price: unknown): number {
  if (price === null || price === undefined) return 0;
  
  // Money object format
  if (typeof price === "object" && price !== null && "amount" in price) {
    const moneyObj = price as { amount: string | number; currency?: string };
    return typeof moneyObj.amount === "string" 
      ? parseFloat(moneyObj.amount) || 0
      : moneyObj.amount || 0;
  }
  
  // String format (djmoney default: "100000.00")
  if (typeof price === "string") {
    return parseFloat(price) || 0;
  }
  
  // Number format
  if (typeof price === "number") {
    return price;
  }
  
  return 0;
}

/**
 * Format price from various formats to currency string
 */
export function formatPrice(
  price: unknown,
  currency: string = "VND"
): string {
  const amount = parsePrice(price);
  
  // Try to get currency from Money object
  if (typeof price === "object" && price !== null && "currency" in price) {
    currency = (price as { currency: string }).currency || currency;
  }
  
  return formatCurrency(amount, currency);
}

/**
 * Get image URL, handling both relative paths and absolute URLs
 * - Absolute URLs (http/https) from cloud storage: return as-is
 * - Relative paths: prepend API URL
 * - null/undefined: return placeholder
 * - Dangerous schemes (javascript:): return placeholder for security
 */
export function getImageUrl(path: string | null | undefined): string {
  if (!path) return "/placeholder.jpg";
  
  // SECURITY: Block dangerous URL schemes to prevent XSS
  const lowerPath = path.toLowerCase().trim();
  if (lowerPath.startsWith("javascript:") || lowerPath.startsWith("vbscript:")) {
    return "/placeholder.jpg";
  }
  
  // Already an absolute URL (e.g., from Cloudinary, S3)
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  
  // Data URL (base64) - only allow image data URLs
  if (path.startsWith("data:")) {
    if (path.startsWith("data:image/")) {
      return path;
    }
    return "/placeholder.jpg";
  }
  
  // Relative path - prepend API URL
  const baseUrl = import.meta.env.VITE_API_URL || "";
  // Remove /api/v1 suffix if present for media URLs
  const mediaBaseUrl = baseUrl.replace(/\/api\/v1\/?$/, "");
  
  // Ensure path starts with /
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${mediaBaseUrl}${normalizedPath}`;
}
