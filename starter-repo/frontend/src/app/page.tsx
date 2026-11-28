"use client";

import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import {
  AlertCircle,
  Check,
  CheckCircle2,
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
import { ReportSharePanel } from "./portals";
import { SymptomSafetyCheck } from "./symptom-safety";
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
  ReportComparison,
  ReportHistoryItem,
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
  1: { title: "Tam cá nguyệt 1", weeks: "từ 1 tuần 0 ngày đến hết 13 tuần 6 ngày", shortWeeks: "tuần 1–13" },
  2: { title: "Tam cá nguyệt 2", weeks: "từ 14 tuần 0 ngày đến hết 28 tuần 6 ngày", shortWeeks: "tuần 14–28" },
  3: { title: "Tam cá nguyệt 3", weeks: "từ 29 tuần 0 ngày trở đi", shortWeeks: "từ tuần 29" },
} as const;

function makeEmptyReport(mode: ReferenceMode = "study"): CBCReport {
  return {
    adult_confirmed: false,
    pregnancy_status: "pregnant",
    gestational_age: "",
    specimen_date: "",
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
    specimen_date: "",
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
  const asText = (value: string | number | null | undefined) => value == null ? "" : String(value);
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
      value: asText(found.value),
      unit: found.unit ?? (preserveMissing ? "" : item.defaultUnit),
      ref_low: asText(found.ref_low),
      ref_high: asText(found.ref_high),
      ref_unit: found.ref_unit ?? (preserveMissing ? "" : item.defaultUnit),
    };
  });
}

function toApiPayload(draft: CBCReport): CBCReport {
  const filledRows = draft.rows
    .filter((r) => (r.value ?? "").trim() !== "")
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
    specimen_date: draft.specimen_date?.trim() || null,
    reference_mode: draft.reference_mode,
    rows: filledRows,
  };
}

function firstComparisonReportId(reports: ReportHistoryItem[], activeSessionId: string, activeDate?: string | null) {
  if (!activeDate) return "";
  return reports.find((item) => item.session_id !== activeSessionId
    && item.specimen_date && item.specimen_date < activeDate)?.session_id || "";
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
  const authEpochRef = useRef(0);
  const [revision, setRevision] = useState(0);
  const [draft, setDraft] = useState<CBCReport>(() => makeEmptyReport("study"));
  const [ocrWarnings, setOcrWarnings] = useState<string[]>([]);
  const [formExpanded, setFormExpanded] = useState(true);
  const [visitBriefOpen, setVisitBriefOpen] = useState(false);
  const formRef = useRef<HTMLElement>(null);
  const assistantRef = useRef<HTMLDivElement | null>(null);
  const doctorPromptRef = useRef<HTMLDivElement | null>(null);
  const visitBriefRef = useRef<HTMLElement | null>(null);

  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [reportHistory, setReportHistory] = useState<ReportHistoryItem[]>([]);
  const [selectedComparisonId, setSelectedComparisonId] = useState("");
  const [comparison, setComparison] = useState<ReportComparison | null>(null);
  const [comparisonError, setComparisonError] = useState("");
  const [comparisonLoading, setComparisonLoading] = useState(false);
  const [doctorPrompt, setDoctorPrompt] = useState("");
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

  const clearAccountData = useCallback(() => {
    setSessionId("");
    setRevision(0);
    setDraft(makeEmptyReport("study"));
    setOcrWarnings([]);
    setFormExpanded(true);
    setVisitBriefOpen(false);
    setAnalysis(null);
    setHistory([]);
    setReportHistory([]);
    setSelectedComparisonId("");
    setComparison(null);
    setComparisonError("");
    setComparisonLoading(false);
    setDoctorPrompt("");
    setReply(null);
    setQuestion("");
    setChatRequestId(null);
    setLastSentQuestion("");
    setBannerError("");
    setLoadingAction(null);
    setAudioUrl(null);
    if (mediaRecorderRef.current?.state === "recording") mediaRecorderRef.current.stop();
    mediaRecorderRef.current = null;
    setRecording(false);
    setSessionModalOpen(false);
    setRestoreInput("");
  }, []);

  const handleLogout = useCallback(() => {
    authEpochRef.current += 1;
    abortInFlight();
    clearAccountData();
    setToken("");
  }, [clearAccountData]);

  const api = useMemo(() => {
    const clientEpoch = authEpochRef.current;
    return createApiClient(() => token, () => {
      if (clientEpoch !== authEpochRef.current) return;
      handleLogout();
      setAuthError("Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại.");
    });
  }, [handleLogout, token]);

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

  useEffect(() => {
    if (formExpanded && analysis) {
      formRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [analysis, formExpanded]);

  function abortInFlight() {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
  }

  async function invalidateIfConfirmed() {
    const requestEpoch = authEpochRef.current;
    abortInFlight();
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
      setAudioUrl(null);
    }
    setReply(null);
    setChatRequestId(null);

    if (analysis && sessionId) {
      setVisitBriefOpen(false);
      setAnalysis(null);
      setHistory([]);
      try {
        const res = await api.invalidateReport(sessionId, revision);
        if (requestEpoch !== authEpochRef.current) return;
        setRevision(res.revision);
        const savedReports = await api.getReportHistory();
        if (requestEpoch !== authEpochRef.current) return;
        setReportHistory(savedReports.reports || []);
      } catch (err) {
        if (requestEpoch === authEpochRef.current && err instanceof ApiError) {
          setBannerError(err.message);
        }
      }
    }
  }

  async function finishSignIn(accessToken: string) {
    const requestEpoch = ++authEpochRef.current;
    abortInFlight();
    clearAccountData();
    const client = createApiClient(() => accessToken, () => {
      if (requestEpoch === authEpochRef.current) handleLogout();
    });
    const session = await client.createSession();
    const savedReports = await client.getReportHistory();
    if (requestEpoch !== authEpochRef.current) return;
    setToken(accessToken);
    setSessionId(session.session_id);
    setRevision(session.revision);
    setReportHistory(savedReports.reports || []);
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
    const requestEpoch = authEpochRef.current;
    abortInFlight();
    setBannerError("");
    setLoadingAction("session");
    try {
      const session = await api.createSession();
      if (requestEpoch !== authEpochRef.current) return;
      setSessionId(session.session_id);
      setRevision(session.revision);
      setDraft(makeEmptyReport("study"));
      setFormExpanded(true);
      setVisitBriefOpen(false);
      setAnalysis(null);
      setReply(null);
      setHistory([]);
      setComparison(null);
      setSelectedComparisonId("");
      setDoctorPrompt("");
      setOcrWarnings([]);
      setQuestion("");
      setChatRequestId(null);
    } catch (err) {
      if (requestEpoch === authEpochRef.current) {
        setBannerError(err instanceof Error ? err.message : "Lỗi tạo phiên mới.");
      }
    } finally {
      if (requestEpoch === authEpochRef.current) setLoadingAction(null);
    }
  }

  async function handleLoadMockTCN2() {
    await invalidateIfConfirmed();
    setFormExpanded(true);
    setVisitBriefOpen(false);
    setBannerError("");
    setOcrWarnings([]);
    setDoctorPrompt("");
    setDraft(makeMockTCN2Report());
  }

  async function handleRestoreSession() {
    const id = restoreInput.trim();
    if (!id) return;
    const requestEpoch = authEpochRef.current;
    abortInFlight();
    setFormExpanded(true);
    setVisitBriefOpen(false);
    setBannerError("");
    setLoadingAction("session");
    try {
      const snap = await api.getSession(id);
      if (requestEpoch !== authEpochRef.current) return;
      setSelectedComparisonId("");
      setDoctorPrompt("");
      setSessionId(snap.session_id);
      setRevision(snap.revision);
      if (snap.report) {
        setDraft({
          ...snap.report,
          specimen_date: snap.report.specimen_date || "",
          rows: normalizeRowsForForm(snap.report.rows, false),
        });
        const [ana, hist] = await Promise.all([
          api.getAnalysis(snap.session_id, snap.revision),
          api.getHistory(snap.session_id),
        ]);
        if (requestEpoch !== authEpochRef.current) return;
        const msgs = hist.messages || [];
        const hasAnalysis = ana.status === "analyzed";
        setAnalysis(hasAnalysis ? ana : null);
        setFormExpanded(!hasAnalysis);
        if (!hasAnalysis) {
          setBannerError(ana.output || "Phiếu này cần được kiểm tra và xác nhận lại.");
        }
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
        setFormExpanded(true);
        setHistory([]);
        setReply(null);
        setBannerError(`Phiên ${snap.session_id} chưa có phiếu nào được xác nhận.`);
      }
      const savedReports = await api.getReportHistory();
      if (requestEpoch !== authEpochRef.current) return;
      setReportHistory(savedReports.reports || []);
      setSelectedComparisonId(firstComparisonReportId(savedReports.reports || [], snap.session_id,
        snap.report?.specimen_date));
      setSessionModalOpen(false);
      setRestoreInput("");
    } catch (err) {
      if (requestEpoch === authEpochRef.current) {
        setBannerError(
          err instanceof Error ? err.message : "Không thể mở phiên này."
        );
      }
    } finally {
      if (requestEpoch === authEpochRef.current) setLoadingAction(null);
    }
  }

  async function handleDeleteCurrentSession() {
    if (!sessionId) return;
    const requestEpoch = authEpochRef.current;
    setLoadingAction("session");
    try {
      await api.deleteSession(sessionId);
      if (requestEpoch !== authEpochRef.current) return;
      const savedReports = await api.getReportHistory();
      if (requestEpoch !== authEpochRef.current) return;
      setReportHistory(savedReports.reports || []);
      setSessionModalOpen(false);
      await handleNewSession();
    } catch (err) {
      if (requestEpoch === authEpochRef.current) {
        setBannerError(err instanceof Error ? err.message : "Không thể xóa phiên.");
      }
    } finally {
      if (requestEpoch === authEpochRef.current) setLoadingAction(null);
    }
  }

  async function handleDeleteSavedReport(reportSessionId: string) {
    if (!window.confirm("Xóa phiếu CBC đã lưu này khỏi lịch sử của tài khoản?")) return;
    const requestEpoch = authEpochRef.current;
    try {
      await api.deleteSession(reportSessionId);
      if (requestEpoch !== authEpochRef.current) return;
      setReportHistory((items) => items.filter((item) => item.session_id !== reportSessionId));
      if (selectedComparisonId === reportSessionId) setSelectedComparisonId("");
      setComparison(null);
      setComparisonError("");
      setDoctorPrompt("");
    } catch (err) {
      if (requestEpoch === authEpochRef.current) {
        setComparisonError(err instanceof Error ? err.message : "Không thể xóa phiếu đã lưu.");
      }
    }
  }

  async function handleImageUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    if (!["image/jpeg", "image/png", "application/pdf"].includes(file.type)) {
      setBannerError("Chị chọn ảnh JPG/PNG hoặc PDF của một phiếu xét nghiệm.");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setBannerError("Ảnh hoặc PDF tối đa 10 MB. Chị chọn tệp nhỏ hơn nhé.");
      return;
    }
    const requestEpoch = authEpochRef.current;
    setFormExpanded(true);
    setVisitBriefOpen(false);

    setBannerError("");
    setOcrWarnings([]);
    setLoadingAction("ocr");

    const controller = new AbortController();
    abortRef.current = controller;
    try {
      const extracted = await api.extractReport(file, controller.signal);
      if (requestEpoch !== authEpochRef.current) return;
      if (!extracted.rows?.length) {
        setOcrWarnings(extracted.warnings || []);
        setBannerError("Chưa đọc được chỉ số CBC từ tệp. Chị thử ảnh rõ hơn hoặc PDF của đúng một phiếu; dữ liệu cũ vẫn được giữ.");
        return;
      }
      await invalidateIfConfirmed();
      if (requestEpoch !== authEpochRef.current) return;
      setOcrWarnings(extracted.warnings || []);
      setDraft((prev) => ({
        ...prev,
        adult_confirmed: false,
        specimen_date: "",
        rows: normalizeRowsForForm(extracted.rows || [], true),
      }));
    } catch (err) {
      if (requestEpoch === authEpochRef.current && (err as Error).name !== "AbortError") {
        setBannerError(
          err instanceof Error ? err.message : "Chưa đọc được tệp phiếu xét nghiệm."
        );
      }
    } finally {
      if (requestEpoch === authEpochRef.current) setLoadingAction(null);
    }
  }

  async function handleConfirm() {
    const requestEpoch = authEpochRef.current;
    setBannerError("");
    setLoadingAction("confirm");
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const payload = toApiPayload(draft);
      const check = await api.validateReport(payload, controller.signal);
      if (requestEpoch !== authEpochRef.current) return;
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
      if (requestEpoch !== authEpochRef.current) return;
      setRevision(res.revision);
      const hasAnalysis = res.analysis.status === "analyzed";
      setAnalysis(hasAnalysis ? res.analysis : null);
      setFormExpanded(!hasAnalysis);
      if (!hasAnalysis) {
        setBannerError(res.analysis.output || "Phiếu cần được kiểm tra lại trước khi xem kết quả.");
      }
      setReply(null);
      setDoctorPrompt("");
      const hist = await api.getHistory(sessionId, controller.signal);
      if (requestEpoch !== authEpochRef.current) return;
      setHistory(hist.messages || []);
      const savedReports = await api.getReportHistory(controller.signal);
      if (requestEpoch !== authEpochRef.current) return;
      setReportHistory(savedReports.reports || []);
      setSelectedComparisonId(firstComparisonReportId(savedReports.reports || [], sessionId,
        payload.specimen_date));
      setComparisonError("");
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
    const requestEpoch = authEpochRef.current;
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
          if (requestEpoch !== authEpochRef.current) return;
          if (text?.trim()) {
            setQuestion(text.trim());
          } else {
            setBannerError(
              "Chưa nhận được lời nói rõ. Bạn có thể ghi lại hoặc gõ câu hỏi."
            );
          }
        } catch (err) {
          if (requestEpoch !== authEpochRef.current) return;
          setBannerError(
            err instanceof Error
              ? err.message
              : "Không thể chuyển giọng nói thành chữ."
          );
        } finally {
          if (requestEpoch === authEpochRef.current) setLoadingAction(null);
        }
      };
      mediaRecorderRef.current = recorder;
      recorder.start();
      setRecording(true);
    } catch {
      if (requestEpoch === authEpochRef.current) {
        setBannerError("Không thể truy cập micro. Vui lòng cấp quyền trình duyệt.");
      }
    }
  }

  async function handleAskAI(e?: React.FormEvent, questionOverride?: string) {
    if (e) e.preventDefault();
    const q = (questionOverride ?? question).trim();
    if (!q || !analysis) return;
    const requestEpoch = authEpochRef.current;

    setBannerError("");
    setQuestion(q);
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
      if (requestEpoch !== authEpochRef.current) return;
      setReply(res);
      if (typeof res.revision === "number") {
        setRevision(res.revision);
      }
      const hist = await api.getHistory(sessionId, controller.signal);
      if (requestEpoch !== authEpochRef.current) return;
      setHistory(hist.messages || []);
      setChatRequestId(null);
    } catch (err) {
      if (requestEpoch === authEpochRef.current && (err as Error).name !== "AbortError") {
        setBannerError(
          err instanceof Error ? err.message : "Không thể nhận câu trả lời từ AI."
        );
      }
    } finally {
      if (requestEpoch === authEpochRef.current) setLoadingAction(null);
    }
  }

  async function handleReadAloud(text: string) {
    const requestEpoch = authEpochRef.current;
    setBannerError("");
    setLoadingAction("tts");
    try {
      const wavBlob = await api.synthesizeWav(text);
      if (requestEpoch !== authEpochRef.current) return;
      if (audioUrl) URL.revokeObjectURL(audioUrl);
      const url = URL.createObjectURL(wavBlob);
      setAudioUrl(url);
    } catch (err) {
      if (requestEpoch !== authEpochRef.current) return;
      setBannerError(
        err instanceof Error ? err.message : "Chưa tạo được giọng đọc."
      );
    } finally {
      if (requestEpoch === authEpochRef.current) setLoadingAction(null);
    }
  }

  function handleDownloadTxt() {
    if (!analysis) return;
    const lines = [
      "KẾT QUẢ ĐỐI CHIẾU CHỈ SỐ CBC THAI KỲ",
      `Ngày lấy mẫu trên phiếu: ${draft.specimen_date || "chưa được nhập"}`,
      `Tuổi thai lúc lấy mẫu: ${draft.gestational_age || "chưa được nhập"}`,
      `Cách chọn khoảng: ${analysis.reference_mode === "study" ? `nghiên cứu theo tam cá nguyệt ${analysis.trimester || "chưa xác định"}` : "khoảng tham chiếu trên phiếu"}`,
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
      ...(analysis.sources || []).map((source) => `${source.title}${source.url ? ` — ${source.url}` : ""}`),
      rowsToReview.length >= 2 ? "\nCÁC DÒNG CẦN TRAO ĐỔI VỚI BÁC SĨ:" : "",
      ...rowsToReview.map((row) => `- ${row.analyte}: ${row.value} ${row.unit} — ${STATUS_META[row.status].label}`),
      `\nCÂU HỎI GỢI Ý CHO BÁC SĨ:\n${doctorPrompt || makeDoctorSummary()}`,
      "\nLưu ý: Tài liệu này tóm tắt đối chiếu tham chiếu, không phải chẩn đoán hoặc hướng dẫn điều trị.",
    ];
    const blob = new Blob([lines.join("\n")], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "ket-qua-doi-chieu-cbc.txt";
    a.click();
    URL.revokeObjectURL(url);
  }

  async function handleDownloadFhir() {
    if (!analysis || !sessionId) return;
    setBannerError("");
    try {
      const bundle = await api.getFhirBundle(sessionId);
      const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: "application/fhir+json;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `cbc-${draft.specimen_date || "phieu"}.fhir.json`;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (reason) {
      setBannerError(reason instanceof Error ? reason.message : "Chưa xuất được tệp FHIR.");
    }
  }

  function updateField<K extends keyof CBCReport>(key: K, value: CBCReport[K]) {
    if (key !== "specimen_date") invalidateIfConfirmed();
    setDoctorPrompt("");
    setDraft((prev) => ({ ...prev, [key]: value }));
  }

  function updateRow(
    analyte: string,
    field: keyof CBCRowInput,
    value: string
  ) {
    invalidateIfConfirmed();
    setDoctorPrompt("");
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
  const draftHasResults = draft.rows.some((row) => (row.value ?? "").trim() !== "");
  const progressStep = analysis?.status === "analyzed" ? 3 : draftHasResults ? 2 : 1;
  const questionRows = rowsToReview.length > 0 ? rowsToReview.slice(0, 2) : resultRows.slice(0, 1);
  const suggestedQuestions = questionRows.map((row) => {
    const name = ANALYTE_LIST.find((item) => item.code === row.analyte)?.name || row.analyte;
    const label = `${row.analyte} (${name})`;
    return row.status === "within"
      ? `${label} của tôi có ổn không?`
      : `${label} ${row.status === "below" ? "thấp" : "cao"} hơn khoảng có ý nghĩa gì?`;
  });
  const flaggedGroups = [
    { title: "Hồng cầu và huyết sắc tố", codes: ["HGB", "RBC", "HCT", "MCV", "MCH", "MCHC"] },
    { title: "Bạch cầu", codes: ["WBC"] },
    { title: "Tiểu cầu", codes: ["PLT"] },
  ].map((group) => ({
    ...group,
    rows: rowsToReview.filter((row) => group.codes.includes(row.analyte)),
  })).filter((group) => group.rows.length > 0);
  const groupQuestion = `Hãy giải thích nhóm chỉ số CBC đã xác nhận: ${rowsToReview.map((row) => `${row.analyte} ${row.value} ${row.unit} ${STATUS_META[row.status].label}`).join("; ")}. Nhóm kết quả này có thể gợi ý điều gì cần trao đổi với bác sĩ? Nêu rõ điều còn chưa thể kết luận từ riêng CBC và câu hỏi phù hợp để hỏi bác sĩ.`;
  const comparableTrendRows = comparison?.rows.filter((row) => row.comparable && row.prior && row.current) || [];
  const changedTrendRows = comparableTrendRows.filter((row) => row.delta !== "0");
  const changedStatusRows = comparableTrendRows.filter((row) => row.prior?.status !== row.current?.status);
  const visitBriefSources = Array.from(new Map(
    [...(analysis?.sources || []), ...(analysis?.reference_source ? [analysis.reference_source] : [])]
      .filter((source) => source.url)
      .map((source) => [source.url!, source] as const)
  ).values());

  function showDoctorPrompt(prompt: string) {
    setDoctorPrompt(prompt);
    requestAnimationFrame(() => doctorPromptRef.current?.scrollIntoView({ behavior: "smooth", block: "center" }));
  }

  function makeDoctorQuestion(row: (typeof resultRows)[number]) {
    const info = ANALYTE_LIST.find((item) => item.code === row.analyte);
    const age = draft.gestational_age ? `Tuổi thai lúc lấy mẫu: ${draft.gestational_age}. ` : "";
    return `${age}Kết quả ${info?.name || row.analyte} (${row.analyte}) của tôi là ${row.value} ${row.unit}, ${STATUS_META[row.status].label.toLowerCase()} theo khoảng đang dùng. Bác sĩ sẽ xem thêm thông tin nào để giải thích kết quả này trong bối cảnh thai kỳ của tôi?`;
  }

  function makeDoctorSummary() {
    const context = [
      draft.gestational_age ? `Tuổi thai lúc lấy mẫu: ${draft.gestational_age}.` : "",
      draft.specimen_date ? `Ngày lấy mẫu: ${draft.specimen_date}.` : "",
    ].filter(Boolean);
    const findings = rowsToReview.map((row) =>
      `${row.analyte} ${row.value} ${row.unit}: ${STATUS_META[row.status].label}`
    );
    return [
      ...context,
      ...findings,
      "",
      "Bác sĩ có thể giải thích các kết quả này khi xem cùng triệu chứng và thông tin sức khỏe của tôi không? Tôi có cần đánh giá thêm điều gì không?",
    ].join("\n");
  }

  function openVisitBrief() {
    setVisitBriefOpen(true);
    requestAnimationFrame(() => visitBriefRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }));
  }

  function printVisitBrief() {
    setVisitBriefOpen(true);
    requestAnimationFrame(() => window.print());
  }

  async function copyDoctorPrompt() {
    if (!doctorPrompt) return;
    try {
      await navigator.clipboard.writeText(doctorPrompt);
      setBannerError("");
    } catch {
      setBannerError("Không sao chép được câu hỏi. Bạn có thể chọn và sao chép nội dung trên màn hình.");
    }
  }
  const otherSavedReports = useMemo(
    () => reportHistory.filter((item) => item.session_id !== sessionId),
    [reportHistory, sessionId]
  );
  const comparableReports = useMemo(
    () => otherSavedReports.filter((item) => Boolean(item.specimen_date)
      && Boolean(draft.specimen_date) && item.specimen_date! < draft.specimen_date!),
    [draft.specimen_date, otherSavedReports]
  );
  const undatedSavedReports = otherSavedReports.filter((item) => !item.specimen_date);
  const sameOrLaterSavedReports = otherSavedReports.filter((item) =>
    item.specimen_date && draft.specimen_date && item.specimen_date >= draft.specimen_date
  );

  useEffect(() => {
    if (!analysis || !sessionId) {
      setComparison(null);
      setComparisonError("");
      setComparisonLoading(false);
      return;
    }
    if (!draft.specimen_date) {
      setComparison(null);
      setComparisonError("Nhập ngày lấy mẫu trên phiếu hiện tại để so sánh theo thời gian.");
      setComparisonLoading(false);
      return;
    }
    const activeSavedReport = reportHistory.find((item) => item.session_id === sessionId);
    if (!activeSavedReport || activeSavedReport.specimen_date !== draft.specimen_date) {
      setComparison(null);
      setComparisonError("Xác nhận ngày lấy mẫu đã nhập trước khi xem so sánh.");
      setComparisonLoading(false);
      return;
    }
    if (!selectedComparisonId) {
      setComparison(null);
      setComparisonError("");
      setComparisonLoading(false);
      return;
    }
    const selected = comparableReports.find((item) => item.session_id === selectedComparisonId);
    if (!selected) {
      setSelectedComparisonId("");
      setComparison(null);
      setComparisonError("");
      setComparisonLoading(false);
      return;
    }
    if (selected.session_id !== selectedComparisonId) setSelectedComparisonId(selected.session_id);
    const controller = new AbortController();
    setComparison(null);
    setComparisonLoading(true);
    setComparisonError("");
    api.compareReports(selected.session_id, sessionId, controller.signal)
      .then((result) => setComparison(result))
      .catch((err) => {
        if ((err as Error).name !== "AbortError") {
          setComparison(null);
          setComparisonError(err instanceof Error ? err.message : "Không thể so sánh hai phiếu.");
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setComparisonLoading(false);
      });
    return () => controller.abort();
  }, [analysis, api, comparableReports, draft.specimen_date, selectedComparisonId, sessionId]);

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
          <p className="text-center text-xs text-[var(--muted)]">
            Bạn là bác sĩ? <Link href="/doctor" className="font-semibold text-[var(--primary)] underline underline-offset-2">Vào cổng bác sĩ</Link>
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
                Nhập hoặc chụp phiếu CBC, xem kết quả đối chiếu và chuẩn bị câu hỏi cho bác sĩ
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
              Thử với phiếu mẫu
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
              onClick={handleLogout}
              className="btn-outline h-9 text-xs"
              title="Đăng xuất"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-[1000px] w-full mx-auto px-4 sm:px-6 py-5 space-y-4">
        <SymptomSafetyCheck />
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

        <div className="space-y-5">
          <section className="soft-card p-4 sm:p-5 space-y-3" aria-label="Tiến trình đọc phiếu CBC">
              <div>
                <h2 className="font-semibold text-base">Cùng đọc phiếu theo 3 bước</h2>
                <p className="mt-1 text-xs text-[var(--muted)]">Bạn có thể chụp phiếu hoặc nhập những dòng kết quả đang có.</p>
              </div>
              <ol className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                {[
                  { number: 1, title: "Thêm phiếu", help: "Chụp ảnh hoặc nhập số liệu" },
                  { number: 2, title: "Kiểm tra", help: "Xem lại thông tin rồi xác nhận" },
                  { number: 3, title: "Hiểu kết quả", help: "Xem đối chiếu và câu hỏi gợi ý" },
                ].map((step) => (
                  <li
                    key={step.number}
                    aria-current={progressStep === step.number ? "step" : undefined}
                    className={`flex gap-2 rounded-xl border p-3 ${progressStep === step.number
                      ? "border-[var(--primary)] bg-[var(--primary-light)]"
                      : "border-[var(--border-strong)] bg-white"}`}
                  >
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border text-xs font-semibold" aria-hidden="true">
                      {progressStep > step.number ? <Check className="h-3.5 w-3.5" /> : step.number}
                    </span>
                    <span>
                      <span className="block text-xs font-semibold">{step.title}</span>
                      <span className="mt-0.5 block text-[11px] text-[var(--muted)]">{step.help}</span>
                      {progressStep === step.number && <span className="sr-only"> — bước hiện tại</span>}
                    </span>
                  </li>
                ))}
              </ol>
          </section>

          {/* Entry form */}
          <section
            ref={formRef}
            id="report-form"
            className={`${analysis && !formExpanded ? "hidden" : ""} soft-card p-4 sm:p-6 space-y-5 scroll-mt-4`}
          >
            <div className="flex items-center justify-between gap-2">
              <h2 className="font-semibold text-[15px]">
                {analysis ? "Chỉnh sửa phiếu CBC" : progressStep === 2 ? "Bước 2 · Kiểm tra phiếu" : "Bước 1 · Thêm phiếu CBC"}
              </h2>
              <span className="text-xs px-2.5 py-1 rounded-full font-medium bg-[var(--primary-light)] text-[var(--primary)]">
                {draft.reference_mode === "study"
                  ? "Theo giai đoạn thai kỳ"
                  : "Theo khoảng trên phiếu"}
              </span>
            </div>

            <div>
              <p className="mb-2 text-xs font-medium">Chọn khoảng để đối chiếu</p>
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
                Khoảng nghiên cứu theo tuổi thai
                <span className="block text-[11px] font-normal text-[var(--muted)] mt-0.5">
                  Hệ thống chọn theo số tuần thai bạn nhập
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
                Khoảng tham chiếu trên phiếu
                <span className="block text-[11px] font-normal text-[var(--muted)] mt-0.5">
                  Bạn nhập giới hạn in cạnh từng chỉ số
                </span>
              </button>
            </div>

            {draft.reference_mode === "study" && (
              <details className="mt-2 rounded-xl border border-[var(--border-strong)] bg-[#f8fafa]">
                <summary className="cursor-pointer select-none p-3 text-xs font-medium">Khoảng nghiên cứu theo tuổi thai là gì?</summary>
                <div className="space-y-2 px-3 pb-3 text-[11px] leading-relaxed text-[var(--muted)]">
                  <p>Tam cá nguyệt là một trong ba giai đoạn của thai kỳ. Tuổi thai ghi theo tuần và ngày, ví dụ 24w2d là 24 tuần 2 ngày. Hệ thống dùng tuổi thai lúc xét nghiệm để chọn giai đoạn: tuần 1–13, tuần 14–28 hoặc từ tuần 29.</p>
                  <p>Đây là khoảng trong một nghiên cứu, không phải ngưỡng chẩn đoán và có thể khác khoảng của phòng xét nghiệm trên phiếu.</p>
                </div>
              </details>
            )}
            </div>

            {/* OCR Upload */}
            <div className="border border-dashed border-[var(--border-strong)] rounded-xl p-3 bg-[#f9fbfb] flex items-center justify-between gap-3">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-lg bg-[var(--primary-light)] text-[var(--primary)] flex items-center justify-center shrink-0">
                  <ImagePlus className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-xs font-medium">
                    Tải phiếu xét nghiệm (JPG, PNG hoặc PDF)
                  </div>
                  <div className="text-[11px] text-[var(--muted)]">
                    Tối đa 10 MB · PDF tối đa 3 trang của cùng một phiếu. AI điền nháp; chị so lại với phiếu gốc trước khi xác nhận.
                  </div>
                </div>
              </div>
              <label className="btn-outline h-8 px-3 text-xs shrink-0 cursor-pointer">
                {loadingAction === "ocr" ? "Đang đọc phiếu..." : "Chọn ảnh / PDF"}
                <input
                  type="file"
                  accept="image/png,image/jpeg,application/pdf,.pdf"
                  className="hidden"
                  onChange={handleImageUpload}
                  disabled={loadingAction === "ocr"}
                />
              </label>
            </div>

            {ocrWarnings.length > 0 && (
              <div className="p-3 rounded-xl bg-[#fffbeb] text-[#b45309] text-xs space-y-1">
                <div className="font-medium">Lưu ý khi đọc phiếu:</div>
                <ul className="list-disc pl-4 space-y-0.5">
                  {ocrWarnings.map((w, idx) => (
                    <li key={idx}>{w}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Context */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
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
                  aria-label="Tuổi thai lúc lấy mẫu, theo tuần và ngày"
                />
              </div>
              <div>
                <label className="block text-xs text-[var(--muted)] mb-1">
                  Ngày lấy mẫu trên phiếu
                </label>
                <input
                  type="date"
                  className="wf-input"
                  value={draft.specimen_date || ""}
                  onChange={(e) => updateField("specimen_date", e.target.value)}
                />
                <p className="mt-1 text-[10px] text-[var(--muted)]">Không bắt buộc. Cần có ngày để so sánh với phiếu trước.</p>
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
                <span>Tôi từ 18 tuổi trở lên</span>
                </label>
              </div>
            </div>

            {/* 8 Analytes */}
            <div className="space-y-2.5">
              <div>
                <h3 className="text-sm font-semibold">Kết quả trên phiếu</h3>
                <p className="mt-1 text-xs text-[var(--muted)]">Chỉ nhập các dòng có trên phiếu. Có thể để trống những chỉ số không có.</p>
              </div>
              <div className="space-y-2 pr-1">
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
                            inputMode="decimal"
                            aria-label={`${item.name} (${item.code}) — kết quả`}
                            value={row.value ?? ""}
                            onChange={(e) =>
                              updateRow(item.code, "value", e.target.value)
                            }
                          />
                        </div>
                        <div className="col-span-4">
                          <input
                            className="wf-input h-8 text-xs"
                            placeholder="Đơn vị"
                            aria-label={`${item.name} (${item.code}) — đơn vị kết quả`}
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
                            inputMode="decimal"
                            aria-label={`${item.name} (${item.code}) — giới hạn dưới trên phiếu`}
                            value={row.ref_low ?? ""}
                            onChange={(e) =>
                              updateRow(item.code, "ref_low", e.target.value)
                            }
                          />
                          <input
                            className="wf-input h-8 text-xs"
                            placeholder="Giới hạn trên"
                            inputMode="decimal"
                            aria-label={`${item.name} (${item.code}) — giới hạn trên trên phiếu`}
                            value={row.ref_high ?? ""}
                            onChange={(e) =>
                              updateRow(item.code, "ref_high", e.target.value)
                            }
                          />
                          <input
                            className="wf-input h-8 text-xs"
                            placeholder="Đơn vị khoảng"
                            aria-label={`${item.name} (${item.code}) — đơn vị khoảng tham chiếu`}
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
                ? "Đang kiểm tra phiếu..."
                : analysis
                  ? "Lưu thay đổi và cập nhật kết quả"
                  : "Kiểm tra phiếu và xem kết quả"}
            </button>
          </section>

          {loadingAction === "confirm" && (
            <section className="soft-card p-6 space-y-4" role="status" aria-live="polite">
              <p className="text-sm font-medium">Đang kiểm tra phiếu và đối chiếu các chỉ số…</p>
              <div className="h-24 bg-[#f2f5f7] rounded-xl animate-pulse" />
            </section>
          )}

          {analysis?.status === "analyzed" && (
            <section id="cbc-results" className="space-y-5" aria-label="Kết quả phiếu CBC">
                {/* Results overview and optional details */}
                <div className="soft-card p-4 sm:p-5 space-y-3.5">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <h2 className="font-semibold text-[15px]">
                        Kết quả đối chiếu CBC
                      </h2>
                      <p className="text-xs text-[var(--muted)] mt-0.5">
                        Đã đối chiếu {resultRows.length} chỉ số
                        {resultStage ? ` với khoảng nghiên cứu cho ${resultStage.title.toLowerCase()} (${resultStage.weeks})` : " với khoảng đã chọn"}.
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <button type="button" onClick={() => setFormExpanded(true)} className="btn-outline h-8 px-3 text-xs" aria-controls="report-form">Sửa thông tin phiếu</button>
                      <button type="button" onClick={openVisitBrief} className="btn-primary h-8 px-3 text-xs">Chuẩn bị nội dung buổi khám</button>
                      <button type="button" onClick={handleDownloadTxt} className="btn-outline h-8 px-3 text-xs"><Download className="w-3.5 h-3.5" /> Tải kết quả</button>
                      <button type="button" onClick={() => void handleDownloadFhir()} className="btn-outline h-8 px-3 text-xs" title="Xuất dữ liệu FHIR R4 cho phiếu đã xác nhận">Xuất FHIR</button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2" aria-label="Tóm tắt trạng thái các chỉ số">
                    {([
                      ["within", "Trong khoảng"], ["below", "Thấp hơn khoảng"], ["above", "Cao hơn khoảng"],
                    ] as const).map(([status, label]) => {
                      const count = resultRows.filter((row) => row.status === status).length;
                      return <div key={status} className={`rounded-xl px-3 py-2 text-xs ${STATUS_META[status].cls}`}><strong className="text-base">{count}</strong><span className="ml-2">{label}</span></div>;
                    })}
                  </div>
                  <p className="text-xs leading-relaxed text-[var(--muted)]">“Trong khoảng” chỉ có nghĩa là con số nằm giữa hai giới hạn đang dùng; “thấp hơn” hoặc “cao hơn” nghĩa là nằm ngoài một giới hạn. Những nhãn này không tự xác định có bệnh hay không. Bác sĩ cần xem phiếu gốc, triệu chứng và tình trạng sức khỏe của bạn.</p>

                  {analysis.issues && analysis.issues.length > 0 && (
                    <p role="status" className="rounded-lg bg-[#fffbeb] p-2.5 text-xs text-[#8a5b10]">
                      Một số dòng chưa thể đối chiếu: {analysis.issues.join("; ")}
                    </p>
                  )}

                  {rowsToReview.length > 0 && (
                    <section className="rounded-xl border border-[#f3d9a7] bg-[#fffbeb] p-3 space-y-3" role="status" aria-live="polite">
                      <div>
                        <h3 className="text-sm font-semibold text-[var(--foreground)]">{rowsToReview.length >= 2 ? "Nhóm chỉ số cần trao đổi với bác sĩ" : "Chỉ số cần trao đổi với bác sĩ"}</h3>
                        <p className="text-xs text-[var(--muted)]">Các dòng dưới đây nằm ngoài khoảng đang dùng. Đây là cảnh báo để xem lại cùng bác sĩ, không phải kết luận có bệnh.</p>
                      </div>
                      {rowsToReview.length >= 2 && (
                        <div className="space-y-2">
                          {flaggedGroups.map((group) => (
                            <div key={group.title} className="rounded-lg bg-white/80 p-2.5 text-xs">
                              <p className="font-semibold">{group.title} · {group.rows.length} dòng cần xem</p>
                              <p className="mt-1 text-[var(--muted)]">
                                {group.title.startsWith("Hồng cầu")
                                  ? "Các chỉ số này mô tả số lượng và đặc điểm hồng cầu. Nếu HGB thấp, bác sĩ có thể đánh giá thêm về thiếu máu và nguyên nhân; riêng CBC không xác định được nguyên nhân."
                                  : group.title === "Bạch cầu"
                                    ? "Bạch cầu tham gia bảo vệ cơ thể. Kết quả cao/thấp không tự chứng minh có nhiễm trùng; cần xem thêm thai kỳ, triệu chứng và các dòng bạch cầu khác."
                                    : "Tiểu cầu tham gia đông máu. Con số ngoài khoảng cần được xem cùng mức độ, diễn biến và bối cảnh sức khỏe."}
                              </p>
                            </div>
                          ))}
                        </div>
                      )}
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
                              <button
                                type="button"
                                className="mt-1 text-[var(--primary)] underline underline-offset-2"
                                onClick={() => showDoctorPrompt(makeDoctorQuestion(row))}
                              >
                                Soạn câu hỏi cho bác sĩ
                              </button>
                            </li>
                          );
                        })}
                      </ul>
                      <div className="flex flex-wrap gap-2">
                        {rowsToReview.length >= 2 && (
                          <button type="button" className="btn-primary min-h-10 px-3 text-xs" disabled={loadingAction === "chat"} onClick={() => { assistantRef.current?.scrollIntoView({ behavior: "smooth", block: "center" }); void handleAskAI(undefined, groupQuestion); }}>
                            {loadingAction === "chat" ? "Đang xem nhóm chỉ số..." : "Nhờ AI giải thích nhóm chỉ số"}
                          </button>
                        )}
                        <button type="button" className="btn-outline min-h-10 px-3 text-xs" onClick={() => showDoctorPrompt(makeDoctorSummary())}>
                          Soạn tóm tắt cho bác sĩ
                        </button>
                      </div>
                    </section>
                  )}

                  {doctorPrompt && (
                    <div ref={doctorPromptRef} className="rounded-xl border border-[var(--primary)] bg-[var(--primary-light)] p-3 space-y-2 scroll-mt-4" role="status" aria-live="polite" tabIndex={-1}>
                      <p className="text-xs font-semibold">Câu hỏi để trao đổi với bác sĩ</p>
                      <p className="text-xs whitespace-pre-line">{doctorPrompt}</p>
                      <button type="button" className="btn-outline min-h-9 px-3 text-xs" onClick={() => void copyDoctorPrompt()}><Copy className="h-3.5 w-3.5" /> Sao chép câu hỏi</button>
                    </div>
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
                                    <button
                                      type="button"
                                      className="mt-1 text-[10px] text-[var(--primary)] underline underline-offset-2"
                                      onClick={() => showDoctorPrompt(makeDoctorQuestion(row))}
                                    >
                                      Soạn câu hỏi cho bác sĩ
                                    </button>
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

                {visitBriefOpen && (
                  <section ref={visitBriefRef} id="visit-brief" className="soft-card p-5 sm:p-7 space-y-4 scroll-mt-4" aria-label="Tóm tắt CBC để trao đổi với bác sĩ">
                    <div className="flex flex-wrap items-start justify-between gap-3 no-print">
                      <div>
                        <h2 className="font-semibold text-base">Tóm tắt phiếu CBC cho buổi khám</h2>
                        <p className="mt-1 text-xs text-[var(--muted)]">Xem lại nội dung rồi in hoặc lưu thành PDF từ hộp thoại in của trình duyệt.</p>
                      </div>
                      <div className="flex gap-2">
                        <button type="button" className="btn-primary" onClick={printVisitBrief}>In / lưu PDF</button>
                        <button type="button" className="btn-outline" onClick={() => setVisitBriefOpen(false)}>Thu gọn</button>
                      </div>
                    </div>
                    <div className="space-y-1">
                      <h1 className="text-xl font-bold">Tóm tắt kết quả CBC</h1>
                      <p className="text-sm">{draft.gestational_age ? `Tuổi thai lúc lấy mẫu: ${draft.gestational_age}. ` : "Chưa nhập tuổi thai. "}{draft.specimen_date ? `Ngày lấy mẫu: ${draft.specimen_date}.` : "Ngày lấy mẫu chưa được nhập."}</p>
                      <p className="text-xs text-[var(--muted)]">{analysis.reference_mode === "study" ? `Khoảng nghiên cứu theo ${resultStage?.title || "giai đoạn thai kỳ"}${resultStage ? ` (${resultStage.weeks})` : ""}.` : "Khoảng tham chiếu do người dùng nhập theo phiếu xét nghiệm."}</p>
                    </div>
                    <p className="rounded-lg bg-[#f8fafa] p-3 text-sm leading-relaxed">{analysis.output}</p>
                    {analysis.issues && analysis.issues.length > 0 && <p className="rounded-lg bg-[#fffbeb] p-3 text-xs">Chưa đối chiếu được một số dòng: {analysis.issues.join("; ")}</p>}
                    <div className="overflow-x-auto border border-[var(--border-strong)] rounded-xl">
                      <table className="w-full text-sm text-left border-collapse">
                        <thead className="bg-[#f8fafa]"><tr><th className="p-2.5">Chỉ số</th><th className="p-2.5">Kết quả</th><th className="p-2.5">Khoảng đã dùng</th><th className="p-2.5">Đối chiếu</th></tr></thead>
                        <tbody className="divide-y divide-[var(--border)]">
                          {resultRows.map((row) => {
                            const info = ANALYTE_LIST.find((item) => item.code === row.analyte);
                            return <tr key={row.analyte}><td className="p-2.5">{info?.name || row.analyte} ({row.analyte})</td><td className="p-2.5">{row.value} {row.unit}</td><td className="p-2.5">{row.ref_low}–{row.ref_high} {row.unit}</td><td className="p-2.5">{STATUS_META[row.status].label}</td></tr>;
                          })}
                        </tbody>
                      </table>
                    </div>
                    {(rowsToReview.length > 0 || doctorPrompt) && <div><h2 className="font-semibold text-sm">Câu hỏi / điểm cần trao đổi với bác sĩ</h2><p className="mt-1 text-sm whitespace-pre-line">{doctorPrompt || makeDoctorSummary()}</p></div>}
                    {(reply?.status === "explained" || reply?.status === "explained_group") && <div><h2 className="font-semibold text-sm">Giải thích từ trợ lý CBC</h2><p className="mt-1 text-sm whitespace-pre-line">{reply.output}</p></div>}
                    {comparison && <div><h2 className="font-semibold text-sm">Thay đổi so với phiếu trước</h2><p className="mt-1 text-sm">So sánh được {comparableTrendRows.length} chỉ số; {changedTrendRows.length} giá trị có thay đổi và {changedStatusRows.length} trạng thái khác nhau theo khoảng dùng ở từng phiếu. Thay đổi số liệu không tự xác định tình trạng sức khỏe.</p>{changedTrendRows.length > 0 && <ul className="mt-1 list-disc pl-5 text-sm">{changedTrendRows.map((row) => <li key={row.analyte}>{row.analyte}: {row.prior_normalized_value} → {row.current_normalized_value} {row.normalized_unit}{row.prior?.status !== row.current?.status ? ` · ${STATUS_META[row.prior!.status].label} → ${STATUS_META[row.current!.status].label}` : ""}</li>)}</ul>}{comparison.reference_context_differs && <p className="mt-1 text-xs">Hai phiếu dùng bối cảnh tham chiếu khác nhau; trạng thái của từng phiếu được giữ riêng theo khoảng đã dùng tại thời điểm đó.</p>}</div>}
                    {visitBriefSources.length > 0 && <div><h2 className="font-semibold text-sm">Nguồn tham khảo</h2><ul className="mt-1 list-disc pl-5 text-xs">{visitBriefSources.map((source) => <li key={source.url}><span>{source.title}</span><span className="ml-1 break-all">{source.url}</span></li>)}</ul></div>}
                    {analysis.reference_note && <p className="border-t border-[var(--border-strong)] pt-3 text-xs text-[var(--muted)]">{analysis.reference_note}</p>}
                    <p className="border-t border-[var(--border-strong)] pt-3 text-xs text-[var(--muted)]">Tài liệu này tóm tắt phép đối chiếu theo khoảng đã chọn, không phải chẩn đoán hay hướng dẫn điều trị. Bác sĩ cần xem phiếu gốc, tuổi thai, triệu chứng, bệnh sử và xét nghiệm liên quan.</p>
                  </section>
                )}

                <div className="soft-card p-4 sm:p-5 space-y-3">
                  <div>
                    <h2 className="font-semibold text-[15px]">Theo dõi giữa các lần xét nghiệm</h2>
                    <p className="mt-1 text-xs text-[var(--muted)]">
                      So sánh các con số theo ngày lấy mẫu. Tăng hoặc giảm chỉ mô tả thay đổi, không tự nói lên tình trạng sức khỏe.
                    </p>
                  </div>
                  <div className="flex flex-wrap items-end gap-2">
                    <label className="flex-1 min-w-[220px] text-xs text-[var(--muted)]">
                      Chọn một phiếu khác đã lưu
                      <select
                        className="wf-input mt-1"
                        value={selectedComparisonId}
                        onChange={(e) => {
                          setSelectedComparisonId(e.target.value);
                          setDoctorPrompt("");
                        }}
                        disabled={comparableReports.length === 0}
                      >
                        <option value="">Chọn phiếu để so sánh</option>
                        {comparableReports.map((item) => (
                          <option key={item.session_id} value={item.session_id}>
                            {new Date(`${item.specimen_date}T00:00:00`).toLocaleDateString("vi-VN")}
                            {item.gestational_age ? ` · ${item.gestational_age}` : ""}
                            {` · ${item.rows.length} chỉ số`}
                          </option>
                        ))}
                      </select>
                    </label>
                    {selectedComparisonId && (
                      <button type="button" className="btn-outline h-10 px-3 text-xs" onClick={() => handleDeleteSavedReport(selectedComparisonId)}>
                        <Trash2 className="w-3.5 h-3.5" /> Xóa phiếu đã chọn
                      </button>
                    )}
                  </div>
                  {undatedSavedReports.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-xs text-[var(--muted)]">
                        {undatedSavedReports.length} phiếu đã lưu chưa có ngày lấy mẫu nên chưa thể xếp theo thời gian. Mở phiếu để bổ sung đúng ngày ghi trên phiếu.
                      </p>
                      {undatedSavedReports.map((item) => (
                        <div key={item.session_id} className="flex flex-wrap items-center justify-between gap-2 rounded-lg bg-[#f8fafa] p-2 text-xs">
                          <span>{item.rows.length} chỉ số CBC · chưa có ngày lấy mẫu</span>
                          <button
                            type="button"
                            className="text-[var(--primary)] underline underline-offset-2"
                            onClick={() => {
                              setRestoreInput(item.session_id);
                              setSessionModalOpen(true);
                            }}
                          >
                            Mở phiếu
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                  {sameOrLaterSavedReports.length > 0 && comparableReports.length === 0 && (
                    <p className="text-xs text-[var(--muted)]">
                      Phiếu đã lưu có ngày cùng ngày hoặc muộn hơn phiếu hiện tại nên không được dùng làm “lần trước”. Hãy mở phiếu có ngày sớm hơn để so sánh theo thứ tự thời gian.
                    </p>
                  )}
                  {otherSavedReports.length === 0 && (
                    <p className="text-xs text-[var(--muted)]">
                      Cần thêm ít nhất một phiếu CBC khác có ngày lấy mẫu để xem các con số thay đổi ra sao giữa hai lần.
                    </p>
                  )}
                  {comparisonLoading && <p className="text-xs text-[var(--muted)]">Đang tải phần so sánh…</p>}
                  {comparisonError && <p role="alert" className="text-xs text-[#b42318]">{comparisonError}</p>}
                  {comparison && (
                    <div className="space-y-3">
                      <p className="text-xs text-[var(--muted)]">
                        {new Date(`${comparison.prior.specimen_date}T00:00:00`).toLocaleDateString("vi-VN")}
                        {` → `}
                        {new Date(`${comparison.current.specimen_date}T00:00:00`).toLocaleDateString("vi-VN")}
                        {` · Tuổi thai: ${comparison.prior.gestational_age} → ${comparison.current.gestational_age}`}
                      </p>
                      <p className="text-[10px] text-[var(--muted)]">Các giá trị so sánh được hiển thị cùng đơn vị chuẩn hóa; trạng thái vẫn dựa trên khoảng của từng phiếu.</p>
                      {comparison.reference_context_differs && (
                        <p className="rounded-lg bg-[#fffbeb] p-2.5 text-xs text-[#8a5b10]">
                          Hai phiếu khác giai đoạn thai kỳ hoặc cách chọn khoảng tham chiếu. Trạng thái của mỗi phiếu được giữ riêng theo khoảng đã dùng lúc đó.
                        </p>
                      )}
                      <div className="rounded-xl border border-[var(--border-strong)] bg-[#f8fafa] p-3 space-y-1.5" role="status" aria-live="polite">
                        <h3 className="text-sm font-semibold">Tóm tắt thay đổi số liệu</h3>
                        {comparableTrendRows.length === 0 ? (
                          <p className="text-xs text-[var(--muted)]">Chưa có chỉ số nào đủ điều kiện để so sánh trực tiếp giữa hai phiếu.</p>
                        ) : (
                          <>
                            <p className="text-xs text-[var(--muted)]">So sánh được {comparableTrendRows.length} chỉ số; {changedTrendRows.length} giá trị có thay đổi{changedStatusRows.length > 0 ? ` và ${changedStatusRows.length} trạng thái khác nhau theo khoảng của từng phiếu` : ""}. Đây là mô tả số liệu, không cho biết một mình tình trạng đang tốt lên hay xấu đi.</p>
                            {changedTrendRows.length > 0 && <ul className="space-y-1 text-xs">{changedTrendRows.slice(0, 4).map((row) => <li key={row.analyte}><strong>{row.analyte}:</strong> {row.prior_normalized_value} → {row.current_normalized_value} {row.normalized_unit}{row.prior && row.current && row.prior.status !== row.current.status ? ` · ${STATUS_META[row.prior.status].label} → ${STATUS_META[row.current.status].label}` : ""}</li>)}</ul>}
                            {changedStatusRows.length > 0 && <p className="text-xs"><strong>Trạng thái đổi:</strong> {changedStatusRows.map((row) => `${row.analyte} (${STATUS_META[row.prior!.status].label} → ${STATUS_META[row.current!.status].label})`).join("; ")}</p>}
                            {changedTrendRows.length > 4 && <p className="text-[10px] text-[var(--muted)]">Còn {changedTrendRows.length - 4} chỉ số thay đổi khác trong bảng bên dưới.</p>}
                          </>
                        )}
                      </div>
                      <div className="overflow-x-auto border border-[var(--border-strong)] rounded-xl">
                        <table className="w-full text-xs text-left border-collapse">
                          <thead className="bg-[#f8fafa] text-[var(--muted)]">
                            <tr>
                              <th className="py-2 px-3 font-medium">Chỉ số</th>
                              <th className="py-2 px-3 font-medium">Lần trước</th>
                              <th className="py-2 px-3 font-medium">Lần sau</th>
                              <th className="py-2 px-3 font-medium">So sánh</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-[var(--border)]">
                            {comparison.rows.map((row) => {
                              const info = ANALYTE_LIST.find((item) => item.code === row.analyte);
                              return (
                                <tr key={row.analyte}>
                                  <td className="py-2 px-3 font-medium">{info?.name || row.analyte} ({row.analyte})</td>
                                  <td className="py-2 px-3">
                                    {row.prior
                                      ? <>{row.comparable ? `${row.prior_normalized_value} ${row.normalized_unit}` : `${row.prior.value} ${row.prior.unit}`}<br /><span className="text-[10px] text-[var(--muted)]">{STATUS_META[row.prior.status].label}</span></>
                                      : row.prior_unavailable
                                        ? <>{row.prior_unavailable.value} {row.prior_unavailable.unit}<br /><span className="text-[10px] text-[#8a5b10]">{row.prior_unavailable.reason}</span></>
                                        : "Không có trên phiếu"}
                                  </td>
                                  <td className="py-2 px-3">
                                    {row.current
                                      ? <>{row.comparable ? `${row.current_normalized_value} ${row.normalized_unit}` : `${row.current.value} ${row.current.unit}`}<br /><span className="text-[10px] text-[var(--muted)]">{STATUS_META[row.current.status].label}</span></>
                                      : row.current_unavailable
                                        ? <>{row.current_unavailable.value} {row.current_unavailable.unit}<br /><span className="text-[10px] text-[#8a5b10]">{row.current_unavailable.reason}</span></>
                                        : "Không có trên phiếu"}
                                  </td>
                                  <td className="py-2 px-3">
                                    {row.comparable
                                      ? `Thay đổi ${row.delta} ${row.delta_unit}`
                                      : row.reason}
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                      <button
                        type="button"
                        className="btn-outline text-xs"
                        onClick={() => {
                          const comparableRows = comparison.rows
                            .filter((row) => row.comparable && row.prior && row.current);
                          const changedValues = comparableRows
                            .filter((row) => row.delta !== "0")
                            .map((row) => `${row.analyte}: ${row.prior_normalized_value} ${row.normalized_unit} → ${row.current_normalized_value} ${row.normalized_unit}`)
                            .join("; ");
                          showDoctorPrompt(
                            `So với phiếu ngày ${comparison.prior.specimen_date}, phiếu ngày ${comparison.current.specimen_date} có các thay đổi số liệu sau: ${changedValues || (comparableRows.length > 0 ? "các chỉ số so sánh được không thay đổi về giá trị" : "không có dòng nào so sánh trực tiếp được")}. Bác sĩ sẽ xem các thay đổi này cùng những thông tin nào để giải thích?`
                          );
                        }}
                      >
                        Soạn câu hỏi về thay đổi giữa hai phiếu
                      </button>
                    </div>
                  )}
                </div>

                {/* Q&A + Voice */}
                <div ref={assistantRef} id="cbc-assistant" className="soft-card p-4 sm:p-5 space-y-3.5 scroll-mt-4">
                  <div className="flex items-center justify-between">
                    <h2 className="font-semibold text-[15px]">
                      Cùng chị hiểu kết quả CBC
                    </h2>
                    <span className="text-[11px] text-[var(--muted)]">
                      Zipformer STT · VieNeu TTS
                    </span>
                  </div>

                  <p className="text-sm leading-relaxed text-[var(--muted)]">Có điều gì trên phiếu khiến chị băn khoăn, chị cứ hỏi nhé. Chị có thể hỏi lại hoặc nhờ em giải thích chậm hơn, từng ý một.</p>
                  <p className="text-xs text-[var(--muted)]">Em là trợ lý AI dựa trên phiếu đã xác nhận để hỗ trợ chị hiểu kết quả và chuẩn bị câu hỏi cho bác sĩ. Lời giải thích chưa được bác sĩ duyệt.</p>
                  <details className="rounded-xl border border-[var(--border-strong)] bg-[#f8fafa]">
                    <summary className="cursor-pointer select-none p-3 text-xs font-semibold">AI làm gì, đã được kiểm chứng đến đâu và nên làm gì nếu thấy sai?</summary>
                    <div className="space-y-2 px-3 pb-3 text-xs leading-relaxed text-[var(--muted)]">
                      <p><strong className="text-[var(--foreground)]">Đọc ảnh:</strong> AI tạo bản nháp; có thể đọc nhầm chữ số, dấu thập phân, đơn vị hoặc khoảng. Hãy so từng ô với phiếu gốc, sửa nếu cần và chỉ xác nhận khi khớp.</p>
                      <p><strong className="text-[var(--foreground)]">Đối chiếu:</strong> phần mềm dùng phép tính để so giá trị đã xác nhận với khoảng đã chọn. Nhãn “trong/thấp/cao hơn khoảng” không phải kết luận có bệnh.</p>
                      <p><strong className="text-[var(--foreground)]">Hỏi đáp:</strong> mô hình tạo câu trả lời theo câu hỏi hiện tại và những lượt trao đổi gần đây của cùng phiếu. Các con số và trạng thái được ứng dụng lấy trực tiếp từ dữ liệu đã xác nhận; lời giải thích của AI chưa được bác sĩ duyệt.</p>
                      <div className="rounded-lg border border-[var(--border-strong)] bg-white p-2.5">
                        <p className="font-semibold text-[var(--foreground)]">Số liệu kiểm chứng hiện có</p>
                        <p className="mt-1">Hồ sơ hiện lưu một lượt cũ ngày 27/11/2026: model Qwen3:4b đạt 19/24 ca tổng hợp (79,2%), có 5 ca không đạt và 0 lỗi kỹ thuật. Đây là tỷ lệ đạt trên bộ ca cố định của phiên bản cũ, không phải độ chính xác lâm sàng và không đại diện cho bản hiện tại.</p>
                        <p className="mt-1">Độ chính xác đọc ảnh và mức đúng lâm sàng của phần giải thích hiện chưa được đo. Chưa có tập phiếu được bác sĩ thẩm định độc lập.</p>
                      </div>
                      <p><strong className="text-[var(--foreground)]">Nếu thấy có thể sai:</strong> đừng dùng câu trả lời để tự chẩn đoán, đổi thuốc hoặc trì hoãn khám. Kiểm tra/sửa theo phiếu gốc; nếu vẫn không khớp, hỏi bác sĩ hoặc cơ sở xét nghiệm. Khi báo nhóm phát triển, không gửi tên, mã bệnh án hay ảnh phiếu qua kênh chưa được phê duyệt.</p>
                    </div>
                  </details>
                  <div className="flex flex-wrap gap-1.5">
                    {[
                      ...suggestedQuestions,
                      "Tóm tắt những điểm tôi nên hỏi bác sĩ",
                    ].map((sampleQ) => (
                      <button
                        key={sampleQ}
                        type="button"
                        onClick={() => { setQuestion(sampleQ); assistantRef.current?.scrollIntoView({ behavior: "smooth", block: "center" }); }}
                        className="text-[11px] px-2.5 py-1 rounded-full bg-[#f4f6f7] hover:bg-[#e7ecee] text-[var(--foreground)] transition"
                      >
                        {sampleQ}
                      </button>
                    ))}
                  </div>

                  <form onSubmit={handleAskAI} className="flex gap-2">
                    <input
                      className="wf-input flex-1"
                      placeholder="Ví dụ: Em lo về HGB, giải thích từng ý giúp em nhé"
                      aria-label="Nhập câu hỏi về phiếu CBC đã xác nhận"
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
                      {loadingAction === "chat" ? "Đang trả lời..." : "Gửi câu hỏi"}
                    </button>
                  </form>

                  {reply && (
                    <div className="p-4 rounded-xl bg-[#f8fafa] border border-[var(--border-strong)] space-y-2.5 text-sm leading-relaxed">
                      {reply.output.startsWith("[AI giả]") && <p className="rounded-lg bg-[#fffbeb] p-2 text-xs text-[#8a5b10]">Đang dùng chế độ AI mô phỏng; câu trả lời này chưa đến từ model AI thật.</p>}
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
                      {reply.verified_facts && reply.verified_facts.length > 0 && (
                        <div className="border-t border-[var(--border-strong)] pt-2">
                          <p className="text-xs font-semibold">Dữ kiện lấy từ phiếu đã xác nhận</p>
                          <div className="mt-1.5 space-y-1.5">
                            {reply.verified_facts.map((fact) => {
                              const info = ANALYTE_LIST.find((item) => item.code === fact.analyte);
                              return (
                                <div key={fact.analyte} className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1 rounded-lg bg-white px-2.5 py-2 text-xs">
                                  <span className="font-medium">{info?.name || fact.analyte} ({fact.analyte})</span>
                                  <span>{fact.value} {fact.unit} · khoảng {fact.ref_low}–{fact.ref_high} {fact.unit}</span>
                                  <span className={`rounded-full px-2 py-0.5 ${STATUS_META[fact.status].cls}`}>{STATUS_META[fact.status].label}</span>
                                </div>
                              );
                            })}
                          </div>
                          <p className="mt-1.5 text-[11px] text-[var(--muted)]">Đây là đối chiếu với khoảng tham chiếu, không phải kết luận chẩn đoán.</p>
                        </div>
                      )}
                      {reply.sources && reply.sources.length > 0 && (
                        <div className="border-t border-[var(--border-strong)] pt-2 text-xs text-[var(--muted)]">
                          <span className="font-medium">Nguồn tham khảo: </span>
                          {reply.sources.map((source, index) => (
                            <React.Fragment key={source.url || source.title}>
                              {index > 0 ? "; " : ""}
                              {source.url
                                ? <a href={source.url} target="_blank" rel="noreferrer" className="text-[var(--primary)] underline underline-offset-2">{source.title}</a>
                                : source.title}
                            </React.Fragment>
                          ))}
                        </div>
                      )}
                      {audioUrl && (
                        <audio controls autoPlay src={audioUrl} className="w-full h-9" />
                      )}
                    </div>
                  )}

                  {history.length > 0 && (
                    <details className="pt-1">
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
            </section>
          )}
        </div>

        <ReportSharePanel api={api} sessionId={sessionId} revision={revision} enabled={Boolean(analysis && sessionId)} />

        <section className="soft-card p-4 sm:p-5 space-y-3">
          <div>
            <h2 className="font-semibold text-[15px]">Phiếu CBC đã lưu trong tài khoản</h2>
            <p className="mt-1 text-xs text-[var(--muted)]">Chỉ bạn mới xem được các phiếu này. Mở một phiếu để xem lại hoặc bổ sung ngày lấy mẫu.</p>
          </div>
          {reportHistory.length === 0 ? (
            <p className="text-xs text-[var(--muted)]">Chưa có phiếu CBC nào được lưu.</p>
          ) : (
            <ul className="space-y-2">
              {reportHistory.map((item) => (
                <li key={item.session_id} className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-[var(--border-strong)] p-3">
                  <div className="text-xs">
                    <p className="font-medium">
                      {item.specimen_date
                        ? new Date(`${item.specimen_date}T00:00:00`).toLocaleDateString("vi-VN")
                        : "Chưa có ngày lấy mẫu"}
                      {item.gestational_age ? ` · Thai ${item.gestational_age}` : ""}
                      {` · ${item.rows.length} chỉ số`}
                      {item.session_id === sessionId ? " · Đang mở" : ""}
                    </p>
                    <p className="mt-0.5 text-[10px] text-[var(--muted)]">Mã phiếu: {item.session_id.slice(0, 8)}</p>
                  </div>
                  {item.session_id !== sessionId && (
                    <div className="flex gap-2">
                      <button
                        type="button"
                        className="btn-outline h-8 px-3 text-xs"
                        onClick={() => {
                          setRestoreInput(item.session_id);
                          setSessionModalOpen(true);
                        }}
                      >
                        Mở phiếu
                      </button>
                      <button
                        type="button"
                        className="btn-outline h-8 px-3 text-xs text-[#be123c]"
                        onClick={() => handleDeleteSavedReport(item.session_id)}
                      >
                        Xóa
                      </button>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>
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
