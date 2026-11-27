"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  AlertCircle,
  Check,
  CheckCircle2,
  ClipboardList,
  Copy,
  Download,
  ExternalLink,
  FileSpreadsheet,
  HeartPulse,
  History,
  ImagePlus,
  LogOut,
  Mic,
  Plus,
  Send,
  Square,
  Trash2,
  Volume2,
  X,
} from "lucide-react";
import { ApiError, createApiClient } from "@/lib/api";
import { toWav16k } from "@/lib/audio";
import type {
  AnalysisResult,
  CBCRowInput,
  CBCReport,
  ChatResult,
  HistoryItem,
  PregnancyStatus,
  ReferenceMode,
  RowStatus,
} from "@/lib/types";

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (options: {
            client_id: string;
            callback: (response: { credential: string }) => void;
          }) => void;
          renderButton: (element: HTMLElement, options: Record<string, string | number>) => void;
        };
      };
    };
  }
}

const ANALYTE_LIST = [
  { code: "HGB", name: "Huyết sắc tố (Hemoglobin)", description: "Nồng độ hemoglobin trong máu.", defaultUnit: "g/dL" },
  { code: "RBC", name: "Số lượng hồng cầu", description: "Số lượng tế bào hồng cầu trong máu.", defaultUnit: "10^12/L" },
  { code: "HCT", name: "Hematocrit", description: "Tỷ lệ thể tích máu do hồng cầu chiếm.", defaultUnit: "%" },
  { code: "MCV", name: "Thể tích trung bình hồng cầu", description: "Kích thước trung bình của hồng cầu.", defaultUnit: "fL" },
  { code: "MCH", name: "Lượng HGB trung bình hồng cầu", description: "Lượng hemoglobin trung bình trong mỗi hồng cầu.", defaultUnit: "pg" },
  { code: "MCHC", name: "Nồng độ HGB trung bình hồng cầu", description: "Nồng độ hemoglobin bên trong hồng cầu.", defaultUnit: "g/dL" },
  { code: "WBC", name: "Tổng số bạch cầu", description: "Số lượng tế bào bạch cầu trong máu.", defaultUnit: "10^9/L" },
  { code: "PLT", name: "Số lượng tiểu cầu", description: "Số lượng tiểu cầu trong máu.", defaultUnit: "10^9/L" },
] as const;

const STATUS_META: Record<RowStatus, { label: string; meaning: string; cls: string }> = {
  below: {
    label: "Thấp hơn khoảng tham chiếu",
    meaning: "Giá trị thấp hơn mức thấp nhất của khoảng đang dùng.",
    cls: "bg-[#fff1f2] text-[#be123c]",
  },
  within: {
    label: "Trong khoảng tham chiếu",
    meaning: "Giá trị từ mức thấp nhất đến mức cao nhất của khoảng đang dùng.",
    cls: "bg-[#f0fdf4] text-[#15803d]",
  },
  above: {
    label: "Cao hơn khoảng tham chiếu",
    meaning: "Giá trị cao hơn mức cao nhất của khoảng đang dùng.",
    cls: "bg-[#fffbeb] text-[#b45309]",
  },
};

const PREGNANCY_STAGE = {
  1: { title: "Giai đoạn 1", weeks: "từ 1 tuần 0 ngày đến hết 13 tuần 6 ngày", shortWeeks: "tuần 1–13" },
  2: { title: "Giai đoạn 2", weeks: "từ 14 tuần 0 ngày đến hết 28 tuần 6 ngày", shortWeeks: "tuần 14–28" },
  3: { title: "Giai đoạn 3", weeks: "từ 29 tuần 0 ngày trở đi", shortWeeks: "từ tuần 29" },
} as const;

function makeEmptyReport(mode: ReferenceMode = "study"): CBCReport {
  return {
    adult_confirmed: false,
    pregnancy_status: "pregnant",
    gestational_age: "",
    reference_mode: mode,
    rows: ANALYTE_LIST.map((item) => ({
      analyte: item.code,
      value: "",
      unit: item.defaultUnit,
      ref_low: "",
      ref_high: "",
      ref_unit: item.defaultUnit,
    })),
  };
}

function pregnancyStageInfo(trimester?: number) {
  if (trimester === 1 || trimester === 2 || trimester === 3) return PREGNANCY_STAGE[trimester];
  return null;
}

function makeMockTCN2Report(): CBCReport {
  return {
    adult_confirmed: true,
    pregnancy_status: "pregnant",
    gestational_age: "24w2d",
    reference_mode: "study",
    rows: [
      { analyte: "HGB", value: "104", unit: "g/L" },
      { analyte: "RBC", value: "3.78", unit: "10^12/L" },
      { analyte: "HCT", value: "31.8", unit: "%" },
      { analyte: "MCV", value: "84.1", unit: "fL" },
      { analyte: "MCH", value: "27.5", unit: "pg" },
      { analyte: "MCHC", value: "32.7", unit: "g/dL" },
      { analyte: "WBC", value: "12.8", unit: "10^9/L" },
      { analyte: "PLT", value: "210", unit: "10^9/L" },
    ],
  };
}

function normalizeRowsForForm(
  incoming: CBCRowInput[],
  preserveMissing = false
): CBCRowInput[] {
  const byCode = new Map(incoming.map((r) => [r.analyte, r]));
  return ANALYTE_LIST.map((item) => {
    const found = byCode.get(item.code);
    if (!found) {
      return {
        analyte: item.code,
        value: "",
        unit: preserveMissing ? "" : item.defaultUnit,
        ref_low: "",
        ref_high: "",
        ref_unit: preserveMissing ? "" : item.defaultUnit,
      };
    }
    return {
      analyte: item.code,
      value: found.value ?? "",
      unit: found.unit ?? (preserveMissing ? "" : item.defaultUnit),
      ref_low: found.ref_low ?? "",
      ref_high: found.ref_high ?? "",
      ref_unit: found.ref_unit ?? (preserveMissing ? "" : item.defaultUnit),
    };
  });
}

function toApiPayload(draft: CBCReport): CBCReport {
  const filledRows = draft.rows
    .filter((r) => (r.value ?? "").trim() !== "" || (r.unit ?? "").trim() !== "")
    .map((r) => {
      if (draft.reference_mode === "study") {
        return {
          analyte: r.analyte,
          value: r.value?.trim() || null,
          unit: r.unit?.trim() || null,
        };
      }
      return {
        analyte: r.analyte,
        value: r.value?.trim() || null,
        unit: r.unit?.trim() || null,
        ref_low: r.ref_low?.trim() || null,
        ref_high: r.ref_high?.trim() || null,
        ref_unit: r.ref_unit?.trim() || null,
      };
    });

  return {
    adult_confirmed: draft.adult_confirmed,
    pregnancy_status: draft.pregnancy_status,
    gestational_age: draft.gestational_age.trim(),
    reference_mode: draft.reference_mode,
    rows: filledRows,
  };
}

export default function HomePage() {
  const [token, setToken] = useState("");
  const [username, setUsername] = useState("demo");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [authError, setAuthError] = useState("");
  const [authLoading, setAuthLoading] = useState(false);
  const googleButtonRef = useRef<HTMLDivElement>(null);

  const [sessionId, setSessionId] = useState("");
  const [revision, setRevision] = useState(0);
  const [draft, setDraft] = useState<CBCReport>(() => makeMockTCN2Report());
  const [ocrWarnings, setOcrWarnings] = useState<string[]>([]);

  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [reply, setReply] = useState<ChatResult | null>(null);

  const [question, setQuestion] = useState("");
  const [chatRequestId, setChatRequestId] = useState<string | null>(null);
  const [lastSentQuestion, setLastSentQuestion] = useState("");

  const [loadingAction, setLoadingAction] = useState<
    "ocr" | "confirm" | "chat" | "stt" | "tts" | "session" | null
  >(null);
  const [bannerError, setBannerError] = useState("");

  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const [sessionModalOpen, setSessionModalOpen] = useState(false);
  const [restoreInput, setRestoreInput] = useState("");
  const [copiedSession, setCopiedSession] = useState(false);

  const abortRef = useRef<AbortController | null>(null);

  const api = useMemo(
    () =>
      createApiClient(
        () => token,
        () => {
          setToken("");
          setAuthError("Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại.");
        }
      ),
    [token]
  );

  useEffect(() => {
    const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID?.trim();
    if (!clientId) return;

    const initializeGoogleButton = () => {
      if (!window.google || !googleButtonRef.current) return;
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: ({ credential }) => {
          void handleGoogleCredential(credential);
        },
      });
      googleButtonRef.current.replaceChildren();
      window.google.accounts.id.renderButton(googleButtonRef.current, {
        theme: "outline",
        size: "large",
        text: "continue_with",
        shape: "rectangular",
        width: 360,
      });
    };

    let script = document.getElementById("google-identity-services") as HTMLScriptElement | null;
    if (!script) {
      script = document.createElement("script");
      script.id = "google-identity-services";
      script.src = "https://accounts.google.com/gsi/client";
      script.async = true;
      script.defer = true;
      script.addEventListener("load", initializeGoogleButton, { once: true });
      document.head.appendChild(script);
    } else if (window.google) {
      initializeGoogleButton();
    } else {
      script.addEventListener("load", initializeGoogleButton, { once: true });
    }
  }, []);

  useEffect(() => {
    return () => {
      if (audioUrl) URL.revokeObjectURL(audioUrl);
    };
  }, [audioUrl]);

  function abortInFlight() {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
  }

  async function invalidateIfConfirmed() {
    abortInFlight();
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
      setAudioUrl(null);
    }
    setReply(null);
    setChatRequestId(null);

    if (analysis && sessionId) {
      setAnalysis(null);
      setHistory([]);
      try {
        const res = await api.invalidateReport(sessionId, revision);
        setRevision(res.revision);
      } catch (err) {
        if (err instanceof ApiError) {
          setBannerError(err.message);
        }
      }
    }
  }

  async function finishSignIn(accessToken: string) {
    const client = createApiClient(() => accessToken, () => setToken(""));
    const session = await client.createSession();
    setToken(accessToken);
    setSessionId(session.session_id);
    setRevision(session.revision);
  }

  async function handleGoogleCredential(credential: string) {
    setAuthError("");
    setAuthLoading(true);
    try {
      const result = await api.loginWithGoogle(credential);
      await finishSignIn(result.access_token);
    } catch (err) {
      setAuthError(err instanceof Error ? err.message : "Đăng nhập Google không thành công.");
    } finally {
      setAuthLoading(false);
    }
  }

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setAuthError("");
    setAuthLoading(true);
    try {
      if (authMode === "register" && password !== passwordConfirm) {
        throw new Error("Hai mật khẩu chưa khớp.");
      }
      const res = authMode === "register"
        ? await api.register(username.trim(), password)
        : await api.login(username.trim(), password);
      await finishSignIn(res.access_token);
    } catch (err) {
      setAuthError(
        err instanceof Error ? err.message : "Đăng nhập không thành công."
      );
    } finally {
      setAuthLoading(false);
    }
  }

  async function handleNewSession() {
    abortInFlight();
    setBannerError("");
    setLoadingAction("session");
    try {
      const session = await api.createSession();
      setSessionId(session.session_id);
      setRevision(session.revision);
      setDraft(makeEmptyReport("study"));
      setAnalysis(null);
      setReply(null);
      setHistory([]);
      setOcrWarnings([]);
      setQuestion("");
      setChatRequestId(null);
    } catch (err) {
      setBannerError(err instanceof Error ? err.message : "Lỗi tạo phiên mới.");
    } finally {
      setLoadingAction(null);
    }
  }

  async function handleLoadMockTCN2() {
    await invalidateIfConfirmed();
    setBannerError("");
    setOcrWarnings([]);
    setDraft(makeMockTCN2Report());
  }

  async function handleRestoreSession() {
    const id = restoreInput.trim();
    if (!id) return;
    abortInFlight();
    setBannerError("");
    setLoadingAction("session");
    try {
      const snap = await api.getSession(id);
      setSessionId(snap.session_id);
      setRevision(snap.revision);
      if (snap.report) {
        setDraft({
          ...snap.report,
          rows: normalizeRowsForForm(snap.report.rows, false),
        });
        const [ana, hist] = await Promise.all([
          api.getAnalysis(snap.session_id, snap.revision),
          api.getHistory(snap.session_id),
        ]);
        const msgs = hist.messages || [];
        setAnalysis(ana);
        setHistory(msgs);
        if (msgs.length > 0) {
          const latest = msgs[msgs.length - 1];
          setQuestion(latest.question);
          setReply(latest.result);
        } else {
          setQuestion("");
          setReply(null);
        }
      } else {
        setDraft(makeEmptyReport("study"));
        setAnalysis(null);
        setHistory([]);
        setReply(null);
        setBannerError(`Phiên ${snap.session_id} chưa có phiếu nào được xác nhận.`);
      }
      setSessionModalOpen(false);
      setRestoreInput("");
    } catch (err) {
      setBannerError(
        err instanceof Error ? err.message : "Không thể mở phiên này."
      );
    } finally {
      setLoadingAction(null);
    }
  }

  async function handleDeleteCurrentSession() {
    if (!sessionId) return;
    setLoadingAction("session");
    try {
      await api.deleteSession(sessionId);
      setSessionModalOpen(false);
      await handleNewSession();
    } catch (err) {
      setBannerError(err instanceof Error ? err.message : "Không thể xóa phiên.");
    } finally {
      setLoadingAction(null);
    }
  }

  async function handleImageUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;

    await invalidateIfConfirmed();
    setBannerError("");
    setOcrWarnings([]);
    setLoadingAction("ocr");

    const controller = new AbortController();
    abortRef.current = controller;
    try {
      const extracted = await api.extractReport(file, controller.signal);
      setOcrWarnings(extracted.warnings || []);
      setDraft((prev) => ({
        ...prev,
        adult_confirmed: false,
        rows: normalizeRowsForForm(extracted.rows || [], true),
      }));
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        setBannerError(
          err instanceof Error ? err.message : "Đọc ảnh thất bại."
        );
      }
    } finally {
      setLoadingAction(null);
    }
  }

  async function handleConfirm() {
    setBannerError("");
    setLoadingAction("confirm");
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const payload = toApiPayload(draft);
      const check = await api.validateReport(payload, controller.signal);
      if (check.status !== "ok" && check.status !== "analyzed") {
        const issueMsg =
          check.issues && check.issues.length > 0
            ? check.issues.join(" ")
            : check.output;
        setBannerError(issueMsg || "Phiếu chưa đủ thông tin hợp lệ.");
        return;
      }
      const res = await api.confirmReport(
        sessionId,
        payload,
        revision,
        controller.signal
      );
      setRevision(res.revision);
      setAnalysis(res.analysis);
      setReply(null);
      const hist = await api.getHistory(sessionId, controller.signal);
      setHistory(hist.messages || []);
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        setBannerError(
          err instanceof Error ? err.message : "Xác nhận phiếu thất bại."
        );
      }
    } finally {
      setLoadingAction(null);
    }
  }

  async function handleToggleRecording() {
    setBannerError("");
    if (recording && mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setRecording(false);
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      audioChunksRef.current = [];
      recorder.ondataavailable = (ev) => {
        if (ev.data.size > 0) audioChunksRef.current.push(ev.data);
      };
      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(audioChunksRef.current, {
          type: recorder.mimeType || "audio/webm",
        });
        setLoadingAction("stt");
        try {
          const wav = await toWav16k(blob);
          const { text } = await api.transcribeWav(wav);
          if (text?.trim()) {
            setQuestion(text.trim());
          } else {
            setBannerError(
              "Chưa nhận được lời nói rõ. Bạn có thể ghi lại hoặc gõ câu hỏi."
            );
          }
        } catch (err) {
          setBannerError(
            err instanceof Error
              ? err.message
              : "Không thể chuyển giọng nói thành chữ."
          );
        } finally {
          setLoadingAction(null);
        }
      };
      mediaRecorderRef.current = recorder;
      recorder.start();
      setRecording(true);
    } catch {
      setBannerError("Không thể truy cập micro. Vui lòng cấp quyền trình duyệt.");
    }
  }

  async function handleAskAI(e?: React.FormEvent) {
    if (e) e.preventDefault();
    const q = question.trim();
    if (!q || !analysis) return;

    setBannerError("");
    setLoadingAction("chat");
    const controller = new AbortController();
    abortRef.current = controller;

    const reqId =
      q === lastSentQuestion && chatRequestId
        ? chatRequestId
        : crypto.randomUUID();
    setLastSentQuestion(q);
    setChatRequestId(reqId);

    try {
      const res = await api.chat(sessionId, q, revision, reqId, controller.signal);
      setReply(res);
      if (typeof res.revision === "number") {
        setRevision(res.revision);
      }
      const hist = await api.getHistory(sessionId, controller.signal);
      setHistory(hist.messages || []);
      setChatRequestId(null);
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        setBannerError(
          err instanceof Error ? err.message : "Không thể nhận câu trả lời từ AI."
        );
      }
    } finally {
      setLoadingAction(null);
    }
  }

  async function handleReadAloud(text: string) {
    setBannerError("");
    setLoadingAction("tts");
    try {
      const wavBlob = await api.synthesizeWav(text);
      if (audioUrl) URL.revokeObjectURL(audioUrl);
      const url = URL.createObjectURL(wavBlob);
      setAudioUrl(url);
    } catch (err) {
      setBannerError(
        err instanceof Error ? err.message : "Chưa tạo được giọng đọc."
      );
    } finally {
      setLoadingAction(null);
    }
  }

  function handleDownloadTxt() {
    if (!analysis) return;
    const lines = [
      "KẾT QUẢ ĐỐI CHIẾU CHỈ SỐ CBC THAI KỲ",
      analysis.output,
      "",
      ...(analysis.rows || []).map(
        (r) =>
          `- ${r.analyte}: ${r.value} ${r.unit} | Khoảng: ${r.ref_low}–${r.ref_high} ${r.unit} | ${STATUS_META[r.status].label}: ${STATUS_META[r.status].meaning}`
      ),
      "",
      analysis.reference_note || "",
      analysis.reference_source?.title || "",
      analysis.reference_source?.url || "",
    ];
    const blob = new Blob([lines.join("\n")], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "ket-qua-doi-chieu-cbc.txt";
    a.click();
    URL.revokeObjectURL(url);
  }

  function updateField<K extends keyof CBCReport>(key: K, value: CBCReport[K]) {
    invalidateIfConfirmed();
    setDraft((prev) => ({ ...prev, [key]: value }));
  }

  function updateRow(
    analyte: string,
    field: keyof CBCRowInput,
    value: string
  ) {
    invalidateIfConfirmed();
    setDraft((prev) => ({
      ...prev,
      rows: prev.rows.map((r) =>
        r.analyte === analyte ? { ...r, [field]: value } : r
      ),
    }));
  }

  const resultStage = pregnancyStageInfo(analysis?.trimester);
  const resultRows = analysis?.rows || [];
  const rowsToReview = resultRows.filter((row) => row.status !== "within");

  if (!token) {
    return (
      <main className="min-h-screen flex items-center justify-center p-4">
        <div className="soft-card w-full max-w-md p-6 space-y-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[var(--primary)] text-white flex items-center justify-center">
              <HeartPulse className="w-5 h-5" />
            </div>
            <div>
              <h1 className="font-semibold text-lg leading-tight">
                Đọc phiếu CBC thai kỳ
              </h1>
              <p className="text-xs text-[var(--muted)]">
                Nhóm 4thangtay · Đăng nhập hoặc tạo tài khoản
              </p>
            </div>
          </div>

          {authError && (
            <div className="p-3 rounded-lg bg-[#fff1f2] text-[#be123c] text-sm flex items-start gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{authError}</span>
            </div>
          )}

          {process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID ? (
            <div className="flex flex-col items-center gap-3">
              <div ref={googleButtonRef} className="min-h-10" />
              <div className="w-full flex items-center gap-3 text-[11px] text-[var(--muted)]">
                <span className="h-px flex-1 bg-[var(--border-strong)]" />
                hoặc đăng nhập bằng email
                <span className="h-px flex-1 bg-[var(--border-strong)]" />
              </div>
            </div>
          ) : (
            <p className="text-xs text-[var(--muted)]">
              Đăng nhập Google sẽ hiện sau khi cấu hình Google Client ID.
            </p>
          )}

          <form onSubmit={handleLogin} className="space-y-3.5">
            <div>
              <label className="block text-xs font-medium text-[var(--muted)] mb-1">
                {authMode === "register" ? "Email" : "Email hoặc tên đăng nhập admin"}
              </label>
              <input
                type={authMode === "register" ? "email" : "text"}
                className="wf-input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder={authMode === "register" ? "ten@example.com" : "Email hoặc tên admin"}
                autoComplete={authMode === "register" ? "email" : "username"}
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-[var(--muted)] mb-1">
                Mật khẩu
              </label>
              <input
                type="password"
                className="wf-input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={authMode === "register" ? "Ít nhất 10 ký tự" : "Nhập mật khẩu"}
                autoComplete={authMode === "register" ? "new-password" : "current-password"}
                required
              />
            </div>
            {authMode === "register" && (
              <div>
                <label className="block text-xs font-medium text-[var(--muted)] mb-1">
                  Nhập lại mật khẩu
                </label>
                <input
                  type="password"
                  className="wf-input"
                  value={passwordConfirm}
                  onChange={(e) => setPasswordConfirm(e.target.value)}
                  autoComplete="new-password"
                  required
                />
              </div>
            )}
            <button
              type="submit"
              className="btn-primary w-full"
              disabled={authLoading}
            >
              {authLoading
                ? "Đang kết nối..."
                : authMode === "register" ? "Tạo tài khoản" : "Đăng nhập"}
            </button>
          </form>
          <p className="text-center text-xs text-[var(--muted)]">
            {authMode === "register" ? "Đã có tài khoản?" : "Chưa có tài khoản?"}{" "}
            <button
              type="button"
              className="font-semibold text-[var(--primary)] underline underline-offset-2"
              onClick={() => {
                setAuthError("");
                setAuthMode(authMode === "register" ? "login" : "register");
                setUsername("");
                setPassword("");
                setPasswordConfirm("");
              }}
            >
              {authMode === "register" ? "Đăng nhập" : "Đăng ký"}
            </button>
          </p>
        </div>
      </main>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white/95 backdrop-blur border-b border-[var(--border-strong)] px-4 sm:px-6 py-3">
        <div className="max-w-[1280px] mx-auto flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-[var(--primary)] text-white flex items-center justify-center shrink-0">
              <HeartPulse className="w-5 h-5" />
            </div>
            <div>
              <h1 className="font-semibold text-base leading-tight">
                Đọc phiếu CBC thai kỳ
              </h1>
              <p className="text-xs text-[var(--muted)]">
                Đối chiếu 8 chỉ số cốt lõi · Hỗ trợ chuẩn bị câu hỏi cho bác sĩ
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={handleLoadMockTCN2}
              className="btn-outline h-9 text-xs"
            >
              <FileSpreadsheet className="w-3.5 h-3.5" />
              Phiếu mẫu TCN2
            </button>
            <button
              type="button"
              onClick={handleNewSession}
              className="btn-outline h-9 text-xs"
            >
              <Plus className="w-3.5 h-3.5" />
              Phiếu mới
            </button>
            <button
              type="button"
              onClick={() => setSessionModalOpen(true)}
              className="btn-outline h-9 text-xs"
            >
              <History className="w-3.5 h-3.5" />
              Phiên ({sessionId.slice(0, 6)})
            </button>
            <button
              type="button"
              onClick={() => setToken("")}
              className="btn-outline h-9 text-xs"
              title="Đăng xuất"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main 2-column Option A */}
      <main className="flex-1 max-w-[1280px] w-full mx-auto px-4 sm:px-6 py-5 space-y-4">
        {bannerError && (
          <div className="p-3.5 rounded-xl bg-[#fff1f2] text-[#be123c] text-sm flex items-start justify-between gap-3">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{bannerError}</span>
            </div>
            <button
              onClick={() => setBannerError("")}
              className="text-xs underline shrink-0"
            >
              Đóng
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
          {/* Left Column (5/12): Form + OCR + Confirm */}
          <section className="lg:col-span-5 soft-card p-4 sm:p-5 space-y-4">
            <div className="flex items-center justify-between gap-2">
              <h2 className="font-semibold text-[15px]">
                Thông tin & Xác nhận phiếu
              </h2>
              <span className="text-xs px-2.5 py-1 rounded-full font-medium bg-[var(--primary-light)] text-[var(--primary)]">
                {draft.reference_mode === "study"
                  ? "Theo giai đoạn thai kỳ"
                  : "Theo khoảng trên phiếu"}
              </span>
            </div>

            {/* Mode selector */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => updateField("reference_mode", "study")}
                className={`p-2.5 rounded-xl border text-left text-xs transition ${
                  draft.reference_mode === "study"
                    ? "border-[var(--primary)] bg-[var(--primary-light)] font-medium text-[var(--primary)]"
                    : "border-[var(--border-strong)] bg-white text-[var(--foreground)]"
                }`}
              >
                Khoảng nghiên cứu theo tuần thai
                <span className="block text-[11px] font-normal text-[var(--muted)] mt-0.5">
                  Tự chọn khoảng theo tuần thai
                </span>
              </button>
              <button
                type="button"
                onClick={() => updateField("reference_mode", "lab")}
                className={`p-2.5 rounded-xl border text-left text-xs transition ${
                  draft.reference_mode === "lab"
                    ? "border-[var(--primary)] bg-[var(--primary-light)] font-medium text-[var(--primary)]"
                    : "border-[var(--border-strong)] bg-white text-[var(--foreground)]"
                }`}
              >
                Khoảng ghi trên phiếu
                <span className="block text-[11px] font-normal text-[var(--muted)] mt-0.5">
                  Tự nhập giới hạn dưới/trên
                </span>
              </button>
            </div>

            {draft.reference_mode === "study" && (
              <div className="rounded-xl bg-[#f8fafa] border border-[var(--border-strong)] p-3 text-[11px] text-[var(--muted)] space-y-1">
                <p className="font-medium text-[var(--foreground)]">
                  Thai kỳ được chia thành ba giai đoạn theo số tuần như sau:
                </p>
                <p>Giai đoạn 1: từ 1 tuần 0 ngày đến hết 13 tuần 6 ngày · Giai đoạn 2: từ 14 tuần 0 ngày đến hết 28 tuần 6 ngày · Giai đoạn 3: từ 29 tuần 0 ngày trở đi.</p>
                <p>Tuổi thai được ghi theo dạng 24w2d, nghĩa là 24 tuần 2 ngày. Khoảng nghiên cứu được chọn theo tuổi thai lúc xét nghiệm.</p>
              </div>
            )}

            {/* OCR Upload */}
            <div className="border border-dashed border-[var(--border-strong)] rounded-xl p-3 bg-[#f9fbfb] flex items-center justify-between gap-3">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-lg bg-[var(--primary-light)] text-[var(--primary)] flex items-center justify-center shrink-0">
                  <ImagePlus className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-xs font-medium">
                    Đọc ảnh phiếu xét nghiệm (JPG/PNG)
                  </div>
                  <div className="text-[11px] text-[var(--muted)]">
                    Ảnh được gửi tới dịch vụ AI để điền nháp; bạn kiểm lại trước khi xác nhận
                  </div>
                </div>
              </div>
              <label className="btn-outline h-8 px-3 text-xs shrink-0 cursor-pointer">
                {loadingAction === "ocr" ? "Đang đọc..." : "Chọn ảnh"}
                <input
                  type="file"
                  accept="image/png,image/jpeg"
                  className="hidden"
                  onChange={handleImageUpload}
                  disabled={loadingAction === "ocr"}
                />
              </label>
            </div>

            {ocrWarnings.length > 0 && (
              <div className="p-3 rounded-xl bg-[#fffbeb] text-[#b45309] text-xs space-y-1">
                <div className="font-medium">Lưu ý khi đọc ảnh:</div>
                <ul className="list-disc pl-4 space-y-0.5">
                  {ocrWarnings.map((w, idx) => (
                    <li key={idx}>{w}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Context */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-xs text-[var(--muted)] mb-1">
                  Tuổi thai lúc xét nghiệm (tuần + ngày)
                </label>
                <input
                  className="wf-input"
                  value={draft.gestational_age}
                  onChange={(e) =>
                    updateField("gestational_age", e.target.value)
                  }
                  placeholder="24w2d (24 tuần 2 ngày)"
                />
              </div>
              <div>
                <label className="block text-xs text-[var(--muted)] mb-1">
                  Tình trạng thai kỳ
                </label>
                <select
                  className="wf-input"
                  value={draft.pregnancy_status}
                  onChange={(e) =>
                    updateField(
                      "pregnancy_status",
                      e.target.value as PregnancyStatus
                    )
                  }
                >
                  <option value="pregnant">Đang mang thai</option>
                  <option value="unknown">Chưa xác định</option>
                  <option value="not_pregnant">Không mang thai</option>
                </select>
              </div>
              <div className="flex items-end pb-2">
                <label className="flex items-center gap-2 text-xs cursor-pointer">
                  <input
                    type="checkbox"
                    checked={draft.adult_confirmed}
                    onChange={(e) =>
                      updateField("adult_confirmed", e.target.checked)
                    }
                    className="accent-[var(--primary)] w-4 h-4"
                  />
                  <span>Xác nhận ≥ 18 tuổi</span>
                </label>
              </div>
            </div>

            {/* 8 Analytes */}
            <div className="space-y-2.5">
              <div className="text-xs font-medium text-[var(--muted)]">
                8 chỉ số CBC hỗ trợ (để trống nếu phiếu không có)
              </div>
              <div className="space-y-2 max-h-[360px] overflow-y-auto pr-1">
                {ANALYTE_LIST.map((item) => {
                  const row = draft.rows.find((r) => r.analyte === item.code) || {
                    analyte: item.code,
                    value: "",
                    unit: "",
                  };
                  return (
                    <div
                      key={item.code}
                      className="p-2.5 rounded-xl bg-[#f8fafa] border border-[var(--border)] space-y-2"
                    >
                      <div className="grid grid-cols-12 gap-2 items-center">
                        <div className="col-span-4">
                          <div className="text-xs font-semibold">{item.code}</div>
                          <div className="text-[11px] text-[var(--muted)] truncate">
                            {item.name}
                          </div>
                        </div>
                        <div className="col-span-4">
                          <input
                            className="wf-input h-8 text-xs"
                            placeholder="Kết quả"
                            value={row.value ?? ""}
                            onChange={(e) =>
                              updateRow(item.code, "value", e.target.value)
                            }
                          />
                        </div>
                        <div className="col-span-4">
                          <input
                            className="wf-input h-8 text-xs"
                            placeholder="Đơn vị *"
                            value={row.unit ?? ""}
                            onChange={(e) =>
                              updateRow(item.code, "unit", e.target.value)
                            }
                          />
                        </div>
                      </div>

                      {draft.reference_mode === "lab" && (
                        <div className="grid grid-cols-3 gap-2">
                          <input
                            className="wf-input h-8 text-xs"
                            placeholder="Giới hạn dưới"
                            value={row.ref_low ?? ""}
                            onChange={(e) =>
                              updateRow(item.code, "ref_low", e.target.value)
                            }
                          />
                          <input
                            className="wf-input h-8 text-xs"
                            placeholder="Giới hạn trên"
                            value={row.ref_high ?? ""}
                            onChange={(e) =>
                              updateRow(item.code, "ref_high", e.target.value)
                            }
                          />
                          <input
                            className="wf-input h-8 text-xs"
                            placeholder="Đơn vị khoảng"
                            value={row.ref_unit ?? ""}
                            onChange={(e) =>
                              updateRow(item.code, "ref_unit", e.target.value)
                            }
                          />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            <button
              type="button"
              onClick={handleConfirm}
              disabled={loadingAction === "confirm" || loadingAction === "ocr"}
              className="btn-primary w-full"
            >
              <CheckCircle2 className="w-4 h-4" />
              {loadingAction === "confirm"
                ? "Đang đối chiếu..."
                : "Xác nhận và nhận kết quả"}
            </button>
          </section>

          {/* Right Column (7/12): Analysis + Q&A + Voice */}
          <section className="lg:col-span-7 space-y-4">
            {loadingAction === "confirm" ? (
              <div className="soft-card p-6 space-y-4 animate-pulse">
                <div className="h-5 bg-[#e4e7ea] rounded w-1/3" />
                <div className="h-32 bg-[#f2f5f7] rounded-xl" />
                <div className="h-12 bg-[#f2f5f7] rounded-xl" />
              </div>
            ) : !analysis ? (
              <div className="soft-card p-8 text-center space-y-3">
                <div className="w-12 h-12 rounded-full bg-[var(--primary-light)] text-[var(--primary)] mx-auto flex items-center justify-center">
                  <ClipboardList className="w-6 h-6" />
                </div>
                <h3 className="font-semibold text-base">
                  Chưa có phiếu được xác nhận
                </h3>
                <p className="text-xs text-[var(--muted)] max-w-md mx-auto leading-relaxed">
                  Kiểm tra lại kết quả, đơn vị và tuổi thai ở cột bên trái, sau
                  đó bấm <strong>Xác nhận và nhận kết quả</strong> để xem bảng đối
                  chiếu và đặt câu hỏi cho AI.
                </p>
                <button
                  type="button"
                  onClick={handleLoadMockTCN2}
                  className="btn-outline text-xs"
                >
                  <FileSpreadsheet className="w-3.5 h-3.5" />
                  Nạp phiếu mẫu giai đoạn 2 (24 tuần 2 ngày)
                </button>
              </div>
            ) : (
              <>
                {/* Results overview and optional details */}
                <div className="soft-card p-4 sm:p-5 space-y-3.5">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <h2 className="font-semibold text-[15px]">
                        Kết quả CBC
                        {resultStage
                          ? ` · ${resultStage.title} (${resultStage.weeks})`
                          : ""}
                      </h2>
                      <p className="text-xs text-[var(--muted)] mt-0.5">
                        {rowsToReview.length > 0
                          ? `Có ${rowsToReview.length}/${resultRows.length} chỉ số nằm ngoài khoảng đang chọn.`
                          : `Cả ${resultRows.length} chỉ số đã nhập đang nằm trong khoảng đang chọn.`}
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={handleDownloadTxt}
                      className="btn-outline h-8 px-3 text-xs"
                    >
                      <Download className="w-3.5 h-3.5" />
                      Tải kết quả
                    </button>
                  </div>

                  <p className="text-xs text-[var(--muted)]">
                    Đây là phép so sánh với khoảng đã chọn, không phải kết luận bệnh. Kết quả trong khoảng cũng không loại trừ bệnh.
                  </p>

                  {rowsToReview.length > 0 && (
                    <section className="rounded-xl border border-[#f3d9a7] bg-[#fffbeb] p-3 space-y-2">
                      <div>
                        <h3 className="text-sm font-semibold text-[var(--foreground)]">Nên hỏi bác sĩ</h3>
                        <p className="text-xs text-[var(--muted)]">Anh/chị có thể ghi lại các dòng này để trao đổi trong buổi khám.</p>
                      </div>
                      <ul className="space-y-2">
                        {rowsToReview.map((row) => {
                          const info = ANALYTE_LIST.find((item) => item.code === row.analyte);
                          return (
                            <li key={row.analyte} className="rounded-lg bg-white/80 p-2.5 text-xs">
                              <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
                                <span className="font-semibold">{info?.name || row.analyte} ({row.analyte})</span>
                                <span>{row.value} {row.unit}</span>
                                <span className={`inline-flex px-2 py-0.5 rounded-full text-[11px] font-medium ${STATUS_META[row.status].cls}`}>
                                  {STATUS_META[row.status].label}
                                </span>
                              </div>
                              <p className="mt-1 text-[var(--muted)]">
                                {info?.description} {STATUS_META[row.status].meaning}
                              </p>
                            </li>
                          );
                        })}
                      </ul>
                    </section>
                  )}

                  <details className="rounded-xl border border-[var(--border-strong)]">
                    <summary className="cursor-pointer select-none p-3 text-sm font-medium">
                      Xem và hiểu đủ {resultRows.length} chỉ số
                    </summary>
                    <div className="px-3 pb-3 space-y-3">
                      <div className="overflow-x-auto border border-[var(--border-strong)] rounded-xl">
                        <table className="w-full text-xs text-left border-collapse">
                          <thead className="bg-[#f8fafa] text-[var(--muted)]">
                            <tr>
                              <th className="py-2.5 px-3 font-medium">Chỉ số</th>
                              <th className="py-2.5 px-3 font-medium">Kết quả</th>
                              <th className="py-2.5 px-3 font-medium">
                                {analysis.reference_mode === "study"
                                  ? "Khoảng nghiên cứu theo giai đoạn"
                                  : "Khoảng trên phiếu"}
                              </th>
                              <th className="py-2.5 px-3 font-medium">So với khoảng</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-[var(--border)]">
                            {resultRows.map((row) => {
                              const info = ANALYTE_LIST.find((item) => item.code === row.analyte);
                              return (
                                <tr key={row.analyte} className="hover:bg-[#f8fafa]">
                                  <td className="py-2.5 px-3">
                                    <div className="font-semibold">{info?.name || row.analyte} ({row.analyte})</div>
                                    {info?.description && (
                                      <p className="mt-1 text-[10px] leading-snug text-[var(--muted)]">{info.description}</p>
                                    )}
                                  </td>
                                  <td className="py-2.5 px-3">{row.value} {row.unit}</td>
                                  <td className="py-2.5 px-3 text-[var(--muted)]">{row.ref_low} – {row.ref_high} {row.unit}</td>
                                  <td className="py-2.5 px-3">
                                    <span className={`inline-flex px-2 py-0.5 rounded-full text-[11px] font-medium ${STATUS_META[row.status].cls}`}>
                                      {STATUS_META[row.status].label}
                                    </span>
                                    <p className="mt-1 text-[10px] leading-snug text-[var(--muted)]">{STATUS_META[row.status].meaning}</p>
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </details>

                  <details className="rounded-xl border border-[var(--border-strong)]">
                    <summary className="cursor-pointer select-none p-3 text-xs font-medium text-[var(--muted)]">
                      Cách đọc kết quả và nguồn tham khảo
                    </summary>
                    <div className="px-3 pb-3 space-y-2 text-[11px] text-[var(--muted)]">
                      <p>“Thấp hơn” nghĩa là dưới mức thấp nhất; “trong khoảng” nghĩa là từ mức thấp nhất đến mức cao nhất; “cao hơn” nghĩa là vượt mức cao nhất của khoảng đang chọn.</p>
                      {analysis.reference_mode === "study" && (
                        <p className="font-medium text-[#7c3aed]">Lưu ý HGB: mức thấp nhất của khoảng nghiên cứu không dùng một mình để kết luận có hay không thiếu máu.</p>
                      )}
                      {(analysis.reference_note || analysis.reference_source) && (
                        <div className="pt-2 border-t border-[var(--border)] space-y-1">
                          {analysis.reference_source && (
                            <div className="font-medium text-[var(--foreground)] flex flex-wrap items-center gap-1.5">
                              <span>Nguồn: {analysis.reference_source.title}</span>
                              {analysis.reference_source.url && (
                                <a
                                  href={analysis.reference_source.url}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="text-[var(--primary)] inline-flex items-center gap-0.5 underline"
                                >
                                  Xem bài báo <ExternalLink className="w-3 h-3" />
                                </a>
                              )}
                            </div>
                          )}
                          {analysis.reference_note && <p>{analysis.reference_note}</p>}
                        </div>
                      )}
                    </div>
                  </details>
                </div>

                {/* Q&A + Voice */}
                <div className="soft-card p-4 sm:p-5 space-y-3.5">
                  <div className="flex items-center justify-between">
                    <h2 className="font-semibold text-[15px]">
                      Hỏi đáp & Gợi ý cho buổi khám
                    </h2>
                    <span className="text-[11px] text-[var(--muted)]">
                      Zipformer STT · VieNeu TTS
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-1.5">
                    {[
                      "Vì sao HGB của mình có dấu thấp?",
                      "Chỉ số WBC này có ý nghĩa gì?",
                      "Tóm tắt các điểm cần hỏi bác sĩ",
                    ].map((sampleQ) => (
                      <button
                        key={sampleQ}
                        type="button"
                        onClick={() => setQuestion(sampleQ)}
                        className="text-[11px] px-2.5 py-1 rounded-full bg-[#f4f6f7] hover:bg-[#e7ecee] text-[var(--foreground)] transition"
                      >
                        {sampleQ}
                      </button>
                    ))}
                  </div>

                  <form onSubmit={handleAskAI} className="flex gap-2">
                    <input
                      className="wf-input flex-1"
                      placeholder="Nhập hoặc ghi âm câu hỏi về chỉ số..."
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                    />
                    <button
                      type="button"
                      onClick={handleToggleRecording}
                      disabled={loadingAction === "stt"}
                      className={`btn-outline px-3 shrink-0 ${
                        recording ? "border-[#be123c] text-[#be123c]" : ""
                      }`}
                      title={
                        recording ? "Dừng ghi âm" : "Ghi âm tiếng Việt (≤ 30s)"
                      }
                    >
                      {recording ? (
                        <Square className="w-4 h-4 fill-current" />
                      ) : (
                        <Mic className="w-4 h-4" />
                      )}
                    </button>
                    <button
                      type="submit"
                      disabled={
                        !question.trim() || loadingAction === "chat"
                      }
                      className="btn-primary shrink-0"
                    >
                      <Send className="w-3.5 h-3.5" />
                      {loadingAction === "chat" ? "Đang trả lời..." : "Hỏi AI"}
                    </button>
                  </form>

                  {reply && (
                    <div className="p-4 rounded-xl bg-[#f8fafa] border border-[var(--border-strong)] space-y-2.5 text-sm leading-relaxed">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-xs font-semibold text-[var(--primary)]">
                          {reply.analyte
                            ? `Giải thích chỉ số ${reply.analyte}`
                            : "Phản hồi từ trợ lý"}
                        </span>
                        <button
                          type="button"
                          onClick={() => handleReadAloud(reply.output)}
                          disabled={loadingAction === "tts"}
                          className="btn-outline h-7 px-2.5 text-xs"
                        >
                          <Volume2 className="w-3.5 h-3.5" />
                          {loadingAction === "tts"
                            ? "Đang tạo audio..."
                            : "Nghe đọc"}
                        </button>
                      </div>
                      <p className="text-[13px] whitespace-pre-line">
                        {reply.output}
                      </p>
                      {audioUrl && (
                        <audio controls autoPlay src={audioUrl} className="w-full h-9" />
                      )}
                    </div>
                  )}

                  {history.length > 0 && (
                    <details open className="pt-1">
                      <summary className="text-xs font-medium text-[var(--muted)] cursor-pointer select-none">
                        Lịch sử hỏi đáp của phiếu ({history.length})
                      </summary>
                      <div className="mt-2.5 space-y-2 max-h-48 overflow-y-auto">
                        {history.map((item, idx) => (
                          <div
                            key={idx}
                            className="p-2.5 rounded-lg bg-[#f8fafa] text-xs space-y-1"
                          >
                            <div className="font-medium">
                              Bạn hỏi: {item.question}
                            </div>
                            <div className="text-[var(--muted)]">
                              {item.result.output}
                            </div>
                          </div>
                        ))}
                      </div>
                    </details>
                  )}
                </div>
              </>
            )}
          </section>
        </div>
      </main>

      {/* Saved Session Modal */}
      {sessionModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/30 flex items-center justify-center p-4">
          <div className="soft-card w-full max-w-md p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-base">Quản lý phiên đã lưu</h3>
              <button
                onClick={() => setSessionModalOpen(false)}
                className="p-1 rounded-lg hover:bg-[var(--item-hover)]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="text-xs space-y-1">
              <div className="text-[var(--muted)]">Mã phiên hiện tại:</div>
              <div className="flex items-center gap-2">
                <code className="flex-1 p-2 rounded-lg bg-[#f4f6f7] font-mono text-xs select-all truncate">
                  {sessionId}
                </code>
                <button
                  type="button"
                  onClick={async () => {
                    await navigator.clipboard.writeText(sessionId);
                    setCopiedSession(true);
                    setTimeout(() => setCopiedSession(false), 2000);
                  }}
                  className="btn-outline h-8 px-2.5 text-xs shrink-0"
                  title="Sao chép mã phiên"
                >
                  {copiedSession ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-[#15803d]" />
                      Đã chép
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      Chép
                    </>
                  )}
                </button>
              </div>
            </div>
            <div className="space-y-2">
              <label className="block text-xs text-[var(--muted)]">
                Mở lại phiên khác bằng mã
              </label>
              <div className="flex gap-2">
                <input
                  className="wf-input flex-1"
                  placeholder="Dán mã phiên..."
                  value={restoreInput}
                  onChange={(e) => setRestoreInput(e.target.value)}
                />
                <button
                  type="button"
                  onClick={handleRestoreSession}
                  className="btn-primary shrink-0"
                >
                  Mở phiên
                </button>
              </div>
            </div>
            <div className="pt-2 border-t border-[var(--border)] flex justify-between items-center">
              <button
                type="button"
                onClick={handleDeleteCurrentSession}
                className="text-xs text-[#be123c] inline-flex items-center gap-1 hover:underline"
              >
                <Trash2 className="w-3.5 h-3.5" />
                Xóa phiên hiện tại
              </button>
              <button
                type="button"
                onClick={() => setSessionModalOpen(false)}
                className="btn-outline h-8 text-xs"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
