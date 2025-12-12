import axios, { AxiosError } from "axios";

// =============================================================================
// 1. TYPE DEFINITIONS
// =============================================================================

/** Mã lỗi tiêu chuẩn để xử lý logic trong code */
export type ApiErrorCode =
  | "authentication_failed" // 401
  | "permission_denied"     // 403
  | "not_found"            // 404
  | "method_not_allowed"   // 405
  | "validation_error"     // 400
  | "throttled"            // 429
  | "server_error"         // 5xx
  | "timeout"              // ECONNABORTED
  | "network_error"        // Network Error
  | "cancelled"            // Request Cancelled
  | "unknown";             // Others

/** Cấu trúc response lỗi chuẩn từ Backend (DRF) */
export interface ApiErrorResponse {
  detail?: string;
  message?: string;
  non_field_errors?: string[];
  errors?: Record<string, string[]>; // Trường hợp bọc lỗi trong object 'errors'
  [key: string]: any; // Để bắt các lỗi field nằm trực tiếp ở root (DRF mặc định)
}

/** Đối tượng lỗi đã được chuẩn hóa để sử dụng trong UI */
export interface ParsedApiError {
  message: string;
  statusCode: number | null;
  code: ApiErrorCode;
  fieldErrors: Record<string, string>;
  isNetworkError: boolean;
  isAuthError: boolean;
  originalError: unknown;
}

// =============================================================================
// 2. CONSTANTS
// =============================================================================

/** Map mã lỗi HTTP sang thông báo mặc định */
const HTTP_STATUS_MESSAGES: Record<number, string> = {
  400: "Dữ liệu không hợp lệ.",
  401: "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.",
  403: "Bạn không có quyền thực hiện hành động này.",
  404: "Không tìm thấy tài nguyên yêu cầu.",
  405: "Phương thức không được phép.",
  429: "Quá nhiều yêu cầu. Vui lòng thử lại sau.",
  500: "Lỗi máy chủ nội bộ.",
  502: "Bad Gateway.",
  503: "Dịch vụ không khả dụng.",
  504: "Gateway Timeout.",
};

// =============================================================================
// 3. CORE LOGIC
// =============================================================================

/**
 * Trích xuất message và field errors từ data trả về
 */
function extractErrorData(data: ApiErrorResponse | null | undefined): {
  message: string | null;
  fieldErrors: Record<string, string>;
} {
  const result = { message: null as string | null, fieldErrors: {} as Record<string, string> };

  if (!data || typeof data !== "object") return result;

  // 1. Ưu tiên lấy message từ 'detail' (DRF mặc định) hoặc 'message'
  if (data.detail) result.message = data.detail;
  else if (data.message) result.message = data.message;
  
  // 2. Xử lý non_field_errors
  else if (Array.isArray(data.non_field_errors) && data.non_field_errors.length > 0) {
    result.message = data.non_field_errors[0];
  }

  // 3. Xử lý Field Errors
  // Case A: Lỗi nằm trong key 'errors' (ví dụ: { errors: { email: [...] } })
  const errorSource = data.errors || data; 

  Object.entries(errorSource).forEach(([key, value]) => {
    // Bỏ qua các key hệ thống
    if (["detail", "message", "non_field_errors", "status_text", "code"].includes(key)) return;

    // Nếu value là mảng chuỗi (DRF Standard: { email: ["Invalid"] })
    if (Array.isArray(value) && value.length > 0 && typeof value[0] === "string") {
      result.fieldErrors[key] = value[0];
      // Nếu chưa có message chính, lấy lỗi của field đầu tiên làm message
      if (!result.message) {
        result.message = `${key}: ${value[0]}`; // Hoặc chỉ lấy value[0] tùy requirement
      }
    }
    // Nếu value là chuỗi
    else if (typeof value === "string") {
      result.fieldErrors[key] = value;
      if (!result.message) result.message = value;
    }
  });

  return result;
}

/**
 * Hàm chính: Parse mọi loại lỗi thành format chuẩn
 */
export function parseApiError(error: unknown): ParsedApiError {
  // 1. Khởi tạo giá trị mặc định
  const parsed: ParsedApiError = {
    message: "Đã xảy ra lỗi không mong muốn",
    statusCode: null,
    code: "unknown",
    fieldErrors: {},
    isNetworkError: false,
    isAuthError: false,
    originalError: error,
  };

  // 2. Nếu không phải Axios Error
  if (!axios.isAxiosError(error)) {
    if (error instanceof Error) {
      parsed.message = error.message;
    }
    return parsed;
  }

  const axiosError = error as AxiosError<ApiErrorResponse>;

  // 3. Xử lý Network/Timeout (Không có response)
  if (!axiosError.response) {
    parsed.isNetworkError = true;
    if (axiosError.code === "ECONNABORTED") {
      parsed.code = "timeout";
      parsed.message = "Yêu cầu quá thời gian chờ. Vui lòng thử lại.";
    } else if (axiosError.code === "ERR_CANCELED") {
      parsed.code = "cancelled";
      parsed.message = "Yêu cầu đã bị hủy.";
    } else {
      parsed.code = "network_error";
      parsed.message = "Không thể kết nối đến máy chủ. Vui lòng kiểm tra mạng.";
    }
    return parsed;
  }

  // 4. Xử lý lỗi từ Server (Có response)
  const { status, data } = axiosError.response;
  parsed.statusCode = status;

  // Xác định Code
  if (status === 400) parsed.code = "validation_error";
  else if (status === 401) parsed.code = "authentication_failed";
  else if (status === 403) parsed.code = "permission_denied";
  else if (status === 404) parsed.code = "not_found";
  else if (status === 405) parsed.code = "method_not_allowed";
  else if (status === 429) parsed.code = "throttled";
  else if (status >= 500) parsed.code = "server_error";

  // Xác định các flag
  if (status === 401) parsed.isAuthError = true;

  // Trích xuất dữ liệu lỗi chi tiết
  const extracted = extractErrorData(data);
  parsed.fieldErrors = extracted.fieldErrors;

  // Quyết định Message cuối cùng:
  // Ưu tiên 1: Message từ server trả về
  // Ưu tiên 2: Message mặc định theo HTTP Status Code
  // Ưu tiên 3: Message mặc định "Lỗi {status}"
  parsed.message = 
    extracted.message || 
    HTTP_STATUS_MESSAGES[status] || 
    `Lỗi hệ thống (${status})`;

  return parsed;
}

// =============================================================================
// 4. UTILITIES (Helpers cho Component)
// =============================================================================

/** Lấy thông báo lỗi hiển thị cho user (Thay thế cho handleApiError cũ) */
export function getErrorMessage(error: unknown): string {
  return parseApiError(error).message;
}

/** Lấy danh sách lỗi validation cho Form */
export function getFieldErrors(error: unknown): Record<string, string> {
  return parseApiError(error).fieldErrors;
}

/** Kiểm tra xem có phải lỗi xác thực (401) để logout không */
export function isAuthError(error: unknown): boolean {
  return parseApiError(error).isAuthError;
}

/** Lấy status code nhanh */
export function getStatusCode(error: unknown): number | null {
  if (axios.isAxiosError(error)) {
    return error.response?.status ?? null;
  }
  return null;
}