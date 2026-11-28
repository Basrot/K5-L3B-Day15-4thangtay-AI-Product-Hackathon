"use client";

import { useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import { createApiClient } from "@/lib/api";
import type { CBCReport } from "@/lib/types";

type Api = ReturnType<typeof createApiClient>;

export function ReportSharePanel({ api, sessionId, revision, enabled }: { api: Api; sessionId: string; revision: number; enabled: boolean }) {
  const [email, setEmail] = useState("");
  const [shares, setShares] = useState<Array<{
    share_id: string; created_at: string; expires_at: string; revoked_at: string | null;
    doctor_email: string; doctor_name: string; specialty: string;
    last_viewed_at: string | null; access_count: number;
  }>>([]);
  const [consent, setConsent] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!enabled || !sessionId) return;
    api.getReportShares(sessionId).then((result) => setShares(result.shares)).catch(() => setShares([]));
  }, [api, enabled, revision, sessionId]);

  async function share() {
    setError(""); setNotice(""); setBusy(true);
    try {
      await api.shareReport(sessionId, email.trim());
      setEmail(""); setConsent(false);
      setShares((await api.getReportShares(sessionId)).shares);
      setNotice("Đã cấp quyền xem phiếu này trong 30 ngày.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Chưa chia sẻ được phiếu.");
    } finally { setBusy(false); }
  }

  async function revoke(shareId: string) {
    setError(""); setBusy(true);
    try {
      await api.revokeReportShare(shareId);
      setShares((await api.getReportShares(sessionId)).shares);
      setNotice("Đã thu hồi quyền xem phiếu.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Chưa thu hồi được quyền xem.");
    } finally { setBusy(false); }
  }

  if (!enabled) return null;
  return (
    <section className="soft-card p-4 sm:p-5 space-y-3" aria-labelledby="share-report-title">
      <div>
        <h2 id="share-report-title" className="font-semibold text-[15px]">Chia sẻ phiếu với bác sĩ</h2>
        <p className="mt-1 text-xs text-[var(--muted)]">Chỉ phiếu đang mở được chia sẻ. Bác sĩ cần có tài khoản đã được xác minh; quyền xem tự hết hạn sau 30 ngày.</p>
      </div>
      <label className="block text-xs font-medium">Email tài khoản bác sĩ
        <input className="wf-input mt-1" type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="bacsi@example.com" />
      </label>
      <label className="flex gap-2 items-start text-xs leading-5">
        <input type="checkbox" checked={consent} onChange={(event) => setConsent(event.target.checked)} className="mt-1" />
        <span>Tôi đồng ý cho bác sĩ này xem phiếu CBC đã xác nhận đang mở, tuổi thai/ngày lấy mẫu và tên hiển thị/email tài khoản của tôi.</span>
      </label>
      <button type="button" className="btn-primary h-9 px-4 text-xs" disabled={!consent || !email.trim() || busy} onClick={() => void share()}>
        {busy ? "Đang xử lý…" : "Cấp quyền xem phiếu"}
      </button>
      {error && <p role="alert" className="text-xs text-[#be123c]">{error}</p>}
      {notice && <p role="status" className="text-xs text-[#15803d]">{notice}</p>}
      {shares.length > 0 && <ul className="space-y-2 border-t border-[var(--border)] pt-3">
        {shares.map((share) => {
          const active = !share.revoked_at && Date.parse(share.expires_at) > Date.now();
          return <li key={share.share_id} className="flex flex-wrap items-center justify-between gap-2 rounded-lg bg-[#f8fafa] p-3 text-xs">
            <span><b>{share.doctor_name}</b> · {share.doctor_email}<br /><span className="text-[var(--muted)]">{active ? `Có quyền đến ${new Date(share.expires_at).toLocaleDateString("vi-VN")}` : "Đã hết hạn hoặc thu hồi"}{share.last_viewed_at ? ` · Đã mở ${share.access_count} lần, gần nhất ${new Date(share.last_viewed_at).toLocaleString("vi-VN")}` : " · Chưa mở phiếu"}</span></span>
            {active && <button type="button" disabled={busy} onClick={() => void revoke(share.share_id)} className="btn-outline h-8 px-3 text-xs text-[#be123c]">Thu hồi</button>}
          </li>;
        })}
      </ul>}
    </section>
  );
}

export function DoctorPortal({ api, onLogout, status, onStatusChange }: {
  api: Api; onLogout: () => void; status: "pending" | "active" | "rejected";
  onStatusChange: (status: "pending" | "active" | "rejected" | null) => void;
}) {
  const [reports, setReports] = useState<Array<{
    share_id: string; session_id: string; shared_at: string; expires_at: string;
    specimen_date: string | null; patient_email: string; patient_name: string;
    gestational_age: string | null; row_count: number | null;
  }>>([]);
  const [selected, setSelected] = useState<{
    share_id: string; session_id: string; revision: number; specimen_date: string | null;
    expires_at: string; patient: { name: string; email: string }; report: CBCReport & { analysis_snapshot?: { rows?: Array<{ analyte: string; value: string; unit: string; ref_low: string; ref_high: string; status: string }> } };
  } | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [refresh, setRefresh] = useState(0);

  useEffect(() => {
    if (status !== "active") return;
    api.getDoctorReports().then((result) => setReports(result.reports)).catch((reason) => setError(reason instanceof Error ? reason.message : "Không tải được phiếu."));
  }, [api, refresh, status]);

  async function openReport(shareId: string) {
    setError(""); setBusy(true);
    try { setSelected(await api.getDoctorReport(shareId)); }
    catch (reason) { setSelected(null); setError(reason instanceof Error ? reason.message : "Không mở được phiếu."); }
    finally { setBusy(false); }
  }

  return <main className="min-h-screen max-w-4xl mx-auto p-4 sm:p-6 space-y-5">
    <header className="soft-card p-5 flex flex-wrap items-center justify-between gap-3">
      <div><p className="text-xs text-[var(--muted)]">Cổng bác sĩ · chỉ phiếu được chia sẻ</p><h1 className="text-xl font-semibold">Phiếu CBC được cấp quyền</h1></div>
      <span className="flex items-center gap-3"><Link href="/" className="text-xs text-[var(--primary)] underline">Trang mẹ bầu</Link><button className="btn-outline h-9 px-3 text-xs" onClick={onLogout}>Đăng xuất</button></span>
    </header>
    {status === "pending" && <section className="soft-card p-5 space-y-2"><h2 className="font-semibold">Hồ sơ đang chờ xác minh</h2><p className="text-sm text-[var(--muted)]">Quản trị viên cần xác minh thông tin hành nghề trước khi tài khoản có thể xem phiếu được chia sẻ.</p><button className="btn-outline h-9 px-3 text-xs" onClick={async () => { try { onStatusChange((await api.getCurrentUser()).doctor_status); } catch (reason) { setError(reason instanceof Error ? reason.message : "Không tải được trạng thái."); } }}>Kiểm tra trạng thái</button></section>}
    {status === "rejected" && <section className="soft-card p-5 space-y-2"><h2 className="font-semibold">Hồ sơ chưa được xác minh</h2><p className="text-sm text-[var(--muted)]">Liên hệ quản trị viên nếu thông tin đăng ký cần được kiểm tra lại.</p></section>}
    {status === "active" && <>
      {error && <p role="alert" className="rounded-lg bg-[#fff1f2] p-3 text-sm text-[#be123c]">{error}</p>}
      {selected ? <section className="soft-card p-5 space-y-4">
        <div className="flex flex-wrap justify-between gap-3"><div><button onClick={() => setSelected(null)} className="text-xs text-[var(--primary)] underline">← Danh sách phiếu</button><h2 className="mt-2 font-semibold">Phiếu được chia sẻ bởi {selected.patient.name || selected.patient.email}</h2><p className="text-xs text-[var(--muted)]">Ngày lấy mẫu: {selected.specimen_date || "Chưa ghi"} · Thai {selected.report.gestational_age || "chưa ghi"} · Quyền xem đến {new Date(selected.expires_at).toLocaleDateString("vi-VN")}</p></div><button className="btn-outline h-8 px-3 text-xs" disabled={busy} onClick={() => { setSelected(null); setRefresh((value) => value + 1); }}>Làm mới</button></div>
        <p className="rounded-lg bg-[#fffbeb] p-3 text-xs text-[#8a5b10]">Thông tin do người dùng xác nhận từ phiếu. Trạng thái tham chiếu không phải chẩn đoán; cần đánh giá cùng bối cảnh lâm sàng.</p>
        <div className="overflow-x-auto"><table className="w-full text-left text-xs"><thead><tr className="border-b"><th className="p-2">Chỉ số</th><th className="p-2">Kết quả</th><th className="p-2">Khoảng đối chiếu</th><th className="p-2">Trạng thái</th></tr></thead><tbody>
          {(selected.report.analysis_snapshot?.rows || []).map((row) => <tr key={row.analyte} className="border-b border-[var(--border)]"><td className="p-2 font-semibold">{row.analyte}</td><td className="p-2">{row.value} {row.unit}</td><td className="p-2">{row.ref_low}–{row.ref_high} {row.unit}</td><td className="p-2">{row.status === "below" ? "Thấp hơn khoảng" : row.status === "above" ? "Cao hơn khoảng" : "Trong khoảng"}</td></tr>)}
        </tbody></table></div>
        <p className="text-[10px] text-[var(--muted)]">Chế độ khoảng: {selected.report.reference_mode === "study" ? "Nghiên cứu theo tam cá nguyệt" : "Khoảng ghi trên phiếu"}. Chỉ xem; cổng không cho sửa dữ liệu bệnh nhân.</p>
      </section> : <section className="soft-card p-5 space-y-3"><div className="flex justify-between gap-2"><h2 className="font-semibold">Danh sách phiếu</h2><button className="text-xs text-[var(--primary)] underline" onClick={() => setRefresh((value) => value + 1)}>Tải lại</button></div>
        {reports.length === 0 ? <p className="text-sm text-[var(--muted)]">Chưa có phiếu nào được chia sẻ cho tài khoản này.</p> : <ul className="space-y-2">{reports.map((report) => <li key={report.share_id} className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-[var(--border-strong)] p-3"><div className="text-xs"><b>{report.patient_name || report.patient_email}</b><p className="text-[var(--muted)]">{report.specimen_date || "Chưa ghi ngày lấy mẫu"} · Thai {report.gestational_age || "chưa ghi"} · {report.row_count || 0} chỉ số</p></div><button className="btn-primary h-8 px-3 text-xs" disabled={busy} onClick={() => void openReport(report.share_id)}>Mở phiếu</button></li>)}</ul>}
      </section>}
    </>}
  </main>;
}

export function DoctorApplication({ api, onSubmitted }: { api: Api; onSubmitted: () => void }) {
  const [form, setForm] = useState({ full_name: "", license_number: "", specialty: "", workplace: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError("");
    try { await api.applyAsDoctor(form); onSubmitted(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Chưa gửi được hồ sơ."); }
    finally { setBusy(false); }
  }
  return <section className="soft-card p-4 sm:p-5 space-y-3"><div><h2 className="font-semibold">Đăng ký tài khoản bác sĩ</h2><p className="mt-1 text-xs text-[var(--muted)]">Cần email đã xác minh bằng Google. Quyền xem phiếu chỉ được bật sau khi quản trị viên kiểm tra giấy phép hành nghề.</p></div>
    <form onSubmit={submit} className="grid gap-3 sm:grid-cols-2">{(["full_name", "license_number", "specialty", "workplace"] as const).map((key) => <label className="text-xs" key={key}>{key === "full_name" ? "Họ tên" : key === "license_number" ? "Số giấy phép hành nghề" : key === "specialty" ? "Chuyên khoa" : "Nơi công tác (không bắt buộc)"}<input className="wf-input mt-1" required={key !== "workplace"} value={form[key]} onChange={(event) => setForm({ ...form, [key]: event.target.value })} /></label>)}
      <div className="sm:col-span-2"><button className="btn-primary h-9 px-4 text-xs" disabled={busy}>{busy ? "Đang gửi…" : "Gửi xác minh"}</button>{error && <p role="alert" className="mt-2 text-xs text-[#be123c]">{error}</p>}</div>
    </form>
  </section>;
}

export function AdminDoctorQueue({ api }: { api: Api }) {
  const [doctors, setDoctors] = useState<Array<{ user_id: string; full_name: string; license_number: string; specialty: string; workplace: string; created_at: string; email: string }>>([]);
  const [error, setError] = useState("");
  const [reload, setReload] = useState(0);
  useEffect(() => { api.getPendingDoctors().then((result) => setDoctors(result.doctors)).catch((reason) => setError(reason instanceof Error ? reason.message : "Không tải được hồ sơ.")); }, [api, reload]);
  async function review(id: string, approved: boolean) {
    setError("");
    try { await api.reviewDoctor(id, approved); setReload((value) => value + 1); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Không cập nhật được hồ sơ."); }
  }
  return <section className="soft-card p-4 sm:p-5 space-y-3"><div><h2 className="font-semibold">Xác minh tài khoản bác sĩ</h2><p className="mt-1 text-xs text-[var(--muted)]">Chỉ duyệt khi đã kiểm tra giấy phép ngoài hệ thống.</p></div>{error && <p role="alert" className="text-xs text-[#be123c]">{error}</p>}{doctors.length === 0 ? <p className="text-xs text-[var(--muted)]">Không có hồ sơ chờ duyệt.</p> : <ul className="space-y-2">{doctors.map((doctor) => <li key={doctor.user_id} className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-[var(--border)] p-3 text-xs"><span><b>{doctor.full_name}</b> · {doctor.email}<br />Giấy phép: {doctor.license_number} · {doctor.specialty} · {doctor.workplace || "Chưa ghi nơi công tác"}</span><span className="flex gap-2"><button className="btn-primary h-8 px-3 text-xs" onClick={() => void review(doctor.user_id, true)}>Xác minh</button><button className="btn-outline h-8 px-3 text-xs text-[#be123c]" onClick={() => void review(doctor.user_id, false)}>Từ chối</button></span></li>)}</ul>}</section>;
}
