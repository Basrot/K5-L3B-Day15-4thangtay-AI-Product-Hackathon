import type {
  AnalysisResult,
  CatalogItem,
  CBCReport,
  ChatResult,
  HistoryItem,
  ReportComparison,
  ReportHistoryItem,
} from "./types";

const BASE_URL = (
  process.env.NEXT_PUBLIC_CBC_API_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

export class ApiError extends Error {
  status: number;
  detail: unknown;
  retryAfter?: string | null;

  constructor(
    status: number,
    message: string,
    detail?: unknown,
    retryAfter?: string | null
  ) {
    super(message);
    this.status = status;
    this.detail = detail;
    this.retryAfter = retryAfter;
  }
}

function friendlyErrorMessage(status: number, detail: unknown, retryAfter?: string | null): string {
  const detailText =
    typeof detail === "string"
      ? detail
      : detail && typeof detail === "object" && "message" in detail
      ? String((detail as { message: unknown }).message)
      : "";

  switch (status) {
    case 401:
      return "Phiên đăng nhập đã hết hạn hoặc sai thông tin. Vui lòng đăng nhập lại.";
    case 404:
      return "Không tìm thấy mã phiên này hoặc phiên đã bị xóa.";
    case 409:
      return "Phiếu đã thay đổi ở nơi khác. Hệ thống cần tải lại phiên bản mới nhất trước khi tiếp tục.";
    case 413:
      return "Tệp tải lên vượt quá giới hạn (ảnh/PDF tối đa 10 MB, WAV tối đa 3 MB).";
    case 422:
      return detailText || "Dữ liệu phiếu chưa hợp lệ. Vui lòng kiểm tra lại các trường đã nhập.";
    case 429:
      return retryAfter
        ? `Hệ thống đang xử lý tác vụ AI khác, vui lòng thử lại sau ${retryAfter} giây.`
        : "Hệ thống đang bận xử lý tác vụ AI, vui lòng thử lại sau ít giây.";
    case 502:
      return detailText || "Dịch vụ AI hoặc giọng nói chưa sẵn sàng. Dữ liệu bạn nhập vẫn được giữ nguyên.";
    case 503:
      return detailText || "Máy chủ chưa sẵn sàng. Chị thử lại sau ít phút.";
    default:
      return detailText || `Lỗi kết nối máy chủ (HTTP ${status}).`;
  }
}

export function createApiClient(
  getToken: () => string,
  onUnauthorized: () => void
) {
  async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
    const headers = new Headers(init.headers);
    const token = getToken();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
    if (init.body && !(init.body instanceof FormData)) {
      headers.set("Content-Type", "application/json");
    }

    const response = await fetch(`${BASE_URL}${path}`, { ...init, headers });
    if (!response.ok) {
      if (response.status === 401) {
        onUnauthorized();
      }
      const retryAfter = response.headers.get("Retry-After");
      const body = await response.json().catch(() => ({}));
      const detail = (body as { detail?: unknown }).detail;
      throw new ApiError(
        response.status,
        friendlyErrorMessage(response.status, detail, retryAfter),
        detail,
        retryAfter
      );
    }

    if (response.status === 204) {
      return null as T;
    }
    if (response.headers.get("Content-Type")?.includes("audio/")) {
      return (await response.blob()) as T;
    }
    return (await response.json()) as T;
  }

  return {
    login: (username: string, password: string) =>
      request<{ access_token: string; token_type: string; expires_in: number }>(
        "/v1/auth/login",
        {
          method: "POST",
          body: JSON.stringify({ username, password }),
        }
      ),

    register: (email: string, password: string) =>
      request<{ access_token: string; token_type: string; expires_in: number }>(
        "/v1/auth/register",
        { method: "POST", body: JSON.stringify({ email, password }) }
      ),

    loginWithGoogle: (credential: string) =>
      request<{ access_token: string; token_type: string; expires_in: number }>(
        "/v1/auth/google",
        { method: "POST", body: JSON.stringify({ credential }) }
      ),

    getCurrentUser: () => request<{
      id: string; email: string | null; display_name: string | null;
      role: string; doctor_status: "pending" | "active" | "rejected" | null;
    }>("/v1/auth/me"),

    applyAsDoctor: (profile: { full_name: string; license_number: string; specialty: string; workplace: string }) =>
      request<{ user_id: string; full_name: string; specialty: string; workplace: string; status: string }>(
        "/v1/doctor/apply", { method: "POST", body: JSON.stringify(profile) }
      ),

    getPendingDoctors: () => request<{ doctors: Array<{
      user_id: string; full_name: string; license_number: string; specialty: string;
      workplace: string; created_at: string; email: string;
    }> }>("/v1/admin/doctors/pending"),

    reviewDoctor: (doctorId: string, approved: boolean) =>
      request<{ user_id: string; status: string }>(`/v1/admin/doctors/${encodeURIComponent(doctorId)}/review`, {
        method: "PUT", body: JSON.stringify({ approved }),
      }),

    getDoctorReports: () => request<{ reports: Array<{
      share_id: string; session_id: string; shared_at: string; expires_at: string;
      specimen_date: string | null; patient_email: string; patient_name: string;
      gestational_age: string | null; row_count: number | null;
    }> }>("/v1/doctor/shared-reports"),

    getDoctorReport: (shareId: string) => request<{
      share_id: string; session_id: string; revision: number; specimen_date: string | null;
      expires_at: string; patient: { name: string; email: string };
      report: CBCReport & { analysis_snapshot?: AnalysisResult };
    }>(`/v1/doctor/shared-reports/${encodeURIComponent(shareId)}`),

    shareReport: (sessionId: string, doctorEmail: string) =>
      request<{ share_id: string; session_id: string; expires_at: string }>(
        `/v1/sessions/${encodeURIComponent(sessionId)}/shares`, {
          method: "POST", body: JSON.stringify({ doctor_email: doctorEmail, consent: true }),
        }
      ),

    getReportShares: (sessionId: string) => request<{ shares: Array<{
      share_id: string; session_id: string; created_at: string; expires_at: string;
      revoked_at: string | null; doctor_email: string; doctor_name: string; specialty: string;
      last_viewed_at: string | null; access_count: number;
    }> }>(`/v1/sessions/${encodeURIComponent(sessionId)}/shares`),

    revokeReportShare: (shareId: string) => request<null>(`/v1/shares/${encodeURIComponent(shareId)}`, { method: "DELETE" }),

    getCatalog: () => request<CatalogItem[]>("/v1/catalog"),

    getReportHistory: (signal?: AbortSignal) =>
      request<{ reports: ReportHistoryItem[] }>("/v1/reports/history", { signal }),

    compareReports: (priorSessionId: string, currentSessionId: string, signal?: AbortSignal) =>
      request<ReportComparison>(
        `/v1/reports/history/${encodeURIComponent(priorSessionId)}/compare?current_session_id=${encodeURIComponent(currentSessionId)}`,
        { signal }
      ),

    createSession: () =>
      request<{ session_id: string; revision: number; report: CBCReport | null }>(
        "/v1/sessions",
        { method: "POST" }
      ),

    getSession: (sessionId: string) =>
      request<{ session_id: string; revision: number; report: CBCReport | null }>(
        `/v1/sessions/${encodeURIComponent(sessionId)}`
      ),

    getFhirBundle: (sessionId: string) => request<Record<string, unknown>>(
      `/v1/sessions/${encodeURIComponent(sessionId)}/fhir`
    ),

    deleteSession: (sessionId: string) =>
      request<null>(`/v1/sessions/${encodeURIComponent(sessionId)}`, {
        method: "DELETE",
      }),

    extractReport: (file: File, signal?: AbortSignal) => {
      const form = new FormData();
      form.append("file", file);
      return request<{
        rows: Array<{
          analyte: string;
          value: string | null;
          unit: string | null;
          ref_low?: string | null;
          ref_high?: string | null;
          ref_unit?: string | null;
        }>;
        warnings: string[];
      }>("/v1/reports/extract", { method: "POST", body: form, signal });
    },

    validateReport: (report: CBCReport, signal?: AbortSignal) =>
      request<AnalysisResult>("/v1/reports/validate", {
        method: "POST",
        body: JSON.stringify(report),
        signal,
      }),

    confirmReport: (
      sessionId: string,
      report: CBCReport,
      expectedRevision: number,
      signal?: AbortSignal
    ) =>
      request<{
        session_id: string;
        revision: number;
        report: CBCReport;
        analysis: AnalysisResult;
      }>(`/v1/sessions/${encodeURIComponent(sessionId)}/report`, {
        method: "PUT",
        body: JSON.stringify({
          report,
          confirmed: true,
          expected_revision: expectedRevision,
        }),
        signal,
      }),

    invalidateReport: (sessionId: string, expectedRevision: number) =>
      request<{ session_id: string; revision: number; report: null }>(
        `/v1/sessions/${encodeURIComponent(sessionId)}/invalidate`,
        {
          method: "POST",
          body: JSON.stringify({ expected_revision: expectedRevision }),
        }
      ),

    getAnalysis: (
      sessionId: string,
      expectedRevision: number,
      signal?: AbortSignal
    ) =>
      request<AnalysisResult>(
        `/v1/sessions/${encodeURIComponent(
          sessionId
        )}/analysis?expected_revision=${expectedRevision}`,
        { signal }
      ),

    getHistory: (sessionId: string, signal?: AbortSignal) =>
      request<{ messages: HistoryItem[] }>(
        `/v1/sessions/${encodeURIComponent(sessionId)}/history`,
        { signal }
      ),

    chat: (
      sessionId: string,
      question: string,
      expectedRevision: number,
      requestId: string,
      signal?: AbortSignal
    ) =>
      request<ChatResult>(
        `/v1/sessions/${encodeURIComponent(sessionId)}/chat`,
        {
          method: "POST",
          body: JSON.stringify({
            question,
            expected_revision: expectedRevision,
            request_id: requestId,
          }),
          signal,
        }
      ),

    transcribeWav: (wavBlob: Blob, signal?: AbortSignal) => {
      const form = new FormData();
      form.append("file", wavBlob, "question.wav");
      return request<{ text: string }>("/v1/speech/transcribe", {
        method: "POST",
        body: form,
        signal,
      });
    },

    synthesizeWav: (text: string, signal?: AbortSignal) =>
      request<Blob>("/v1/speech/synthesize", {
        method: "POST",
        body: JSON.stringify({ text }),
        signal,
      }),
  };
}
