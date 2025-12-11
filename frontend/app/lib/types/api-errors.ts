import { AxiosError } from "axios";

/**
 * Standard API error response from Django REST Framework
 */
export interface ApiErrorResponse {
  /** General error message */
  detail?: string;
  /** Alternative error message field */
  message?: string;
  /** Field-specific validation errors */
  errors?: Record<string, string[]>;
  /** Non-field errors array */
  non_field_errors?: string[];
  /** HTTP status code text */
  status_text?: string;
  /** Error code for programmatic handling */
  code?: string;
}

/**
 * Specific error types for different scenarios
 */
export type ApiErrorCode =
  | "authentication_failed"
  | "not_authenticated"
  | "permission_denied"
  | "not_found"
  | "method_not_allowed"
  | "validation_error"
  | "throttled"
  | "server_error"
  | "network_error"
  | "timeout"
  | "unknown";

/**
 * Typed API error that extends AxiosError with our error response
 */
export type TypedApiError = AxiosError<ApiErrorResponse>;

/**
 * Structured error object for use in components
 */
export interface ParsedApiError {
  /** Main error message to display */
  message: string;
  /** HTTP status code */
  statusCode: number | null;
  /** Error code for programmatic handling */
  code: ApiErrorCode;
  /** Field-specific errors for form validation */
  fieldErrors: Record<string, string>;
  /** Whether the error is a network/connectivity issue */
  isNetworkError: boolean;
  /** Whether the error requires re-authentication */
  isAuthError: boolean;
  /** Original error for logging */
  originalError: unknown;
}

/**
 * Parse an API error into a structured format
 */
export function parseApiError(error: unknown): ParsedApiError {
  // Default error structure
  const result: ParsedApiError = {
    message: "Đã xảy ra lỗi không mong muốn",
    statusCode: null,
    code: "unknown",
    fieldErrors: {},
    isNetworkError: false,
    isAuthError: false,
    originalError: error,
  };

  // Not an Axios error
  if (!(error instanceof AxiosError)) {
    if (error instanceof Error) {
      result.message = error.message;
    }
    return result;
  }

  const axiosError = error as TypedApiError;

  // Network error (no response)
  if (!axiosError.response) {
    if (axiosError.code === "ECONNABORTED") {
      result.message = "Yêu cầu quá thời gian chờ. Vui lòng thử lại.";
      result.code = "timeout";
    } else {
      result.message = "Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối mạng.";
      result.code = "network_error";
    }
    result.isNetworkError = true;
    return result;
  }

  const { status, data } = axiosError.response;
  result.statusCode = status;

  // Handle based on status code
  switch (status) {
    case 400:
      result.code = "validation_error";
      result.message = "Dữ liệu không hợp lệ";

      // Extract field errors
      if (data?.errors) {
        for (const [field, messages] of Object.entries(data.errors)) {
          if (Array.isArray(messages) && messages.length > 0) {
            result.fieldErrors[field] = messages[0];
          }
        }
        // Get first error message as main message
        const firstField = Object.keys(data.errors)[0];
        if (firstField && data.errors[firstField]?.[0]) {
          result.message = data.errors[firstField][0];
        }
      }

      // Handle non_field_errors
      if (data?.non_field_errors?.length) {
        result.message = data.non_field_errors[0];
      }

      // Use detail or message if available
      if (data?.detail) {
        result.message = data.detail;
      } else if (data?.message) {
        result.message = data.message;
      }
      break;

    case 401:
      result.code = "not_authenticated";
      result.message = data?.detail || "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.";
      result.isAuthError = true;
      break;

    case 403:
      result.code = "permission_denied";
      result.message = data?.detail || "Bạn không có quyền thực hiện hành động này.";
      break;

    case 404:
      result.code = "not_found";
      result.message = data?.detail || "Không tìm thấy tài nguyên yêu cầu.";
      break;

    case 405:
      result.code = "method_not_allowed";
      result.message = "Phương thức không được phép.";
      break;

    case 429:
      result.code = "throttled";
      result.message = data?.detail || "Quá nhiều yêu cầu. Vui lòng thử lại sau.";
      break;

    case 500:
    case 502:
    case 503:
    case 504:
      result.code = "server_error";
      result.message = "Lỗi máy chủ. Vui lòng thử lại sau.";
      break;

    default:
      result.message = data?.detail || data?.message || `Lỗi ${status}`;
  }

  return result;
}

/**
 * Get user-friendly error message from an API error
 */
export function getErrorMessage(error: unknown): string {
  return parseApiError(error).message;
}

/**
 * Check if error is an authentication error that requires re-login
 */
export function isAuthError(error: unknown): boolean {
  return parseApiError(error).isAuthError;
}

/**
 * Check if error is a network connectivity error
 */
export function isNetworkError(error: unknown): boolean {
  return parseApiError(error).isNetworkError;
}

/**
 * Get field validation errors from an API error
 */
export function getFieldErrors(error: unknown): Record<string, string> {
  return parseApiError(error).fieldErrors;
}

/**
 * Type guard to check if an error is an Axios error with response
 */
export function isApiError(error: unknown): error is TypedApiError {
  return error instanceof AxiosError && error.response !== undefined;
}

/**
 * Extract status code from error
 */
export function getStatusCode(error: unknown): number | null {
  if (isApiError(error)) {
    return error.response?.status ?? null;
  }
  return null;
}
