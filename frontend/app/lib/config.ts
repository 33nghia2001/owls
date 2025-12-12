/**
 * System configuration fetched from backend API
 * Avoids hardcoding values and ensures frontend/backend consistency
 */

export interface SystemConfig {
  shipping: {
    free_shipping_threshold: number;
    default_shipping_cost: number;
  };
  currency: {
    code: string;
    symbol: string;
    decimal_places: number;
  };
  order: {
    max_pending_orders: number;
  };
  file_upload: {
    max_image_size_mb: number;
    allowed_image_types: string[];
  };
}

let cachedConfig: SystemConfig | null = null;

/**
 * Fetch system configuration from backend
 * Uses cache to avoid repeated API calls
 */
export async function fetchSystemConfig(): Promise<SystemConfig> {
  if (cachedConfig) {
    return cachedConfig;
  }

  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";
  const response = await fetch(`${API_URL}/config/`, {
    credentials: 'include', // Send cookies
  });

  if (!response.ok) {
    throw new Error('Failed to fetch system configuration');
  }

  cachedConfig = await response.json();
  return cachedConfig as SystemConfig;
}

/**
 * Get cached config or fetch if not available
 * Use this in loaders/actions that need config values
 */
export async function getConfig(): Promise<SystemConfig> {
  return fetchSystemConfig();
}

/**
 * Clear config cache (useful after settings changes)
 */
export function clearConfigCache(): void {
  cachedConfig = null;
}
