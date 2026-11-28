"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import { HeartPulse } from "lucide-react";
import { ApiError, createApiClient } from "@/lib/api";
import { AdminDoctorQueue, DoctorApplication, DoctorPortal } from "../portals";

type UserProfile = {
  id: string;
  email: string | null;
  display_name: string | null;
  role: string;
  doctor_status: "pending" | "active" | "rejected" | null;
};

export default function DoctorPage() {
  const [token, setToken] = useState("");
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const googleButtonRef = useRef<HTMLDivElement>(null);

  const api = useMemo(() => createApiClient(() => token, () => {
    setToken("");
    setProfile(null);
    setError("Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.");
  }), [token]);

  async function finishSignIn(accessToken: string) {
    const client = createApiClient(() => accessToken, () => {
      setToken("");
      setProfile(null);
    });
    const current = await client.getCurrentUser();
    setToken(accessToken);
    setProfile(current);
    setPassword("");
    setError("");
  }

  async function handleGoogleCredential(credential: string) {
    setBusy(true);
    setError("");
    try {
      const result = await api.loginWithGoogle(credential);
      await finishSignIn(result.access_token);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Đăng nhập Google không thành công.");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID?.trim();
    if (!clientId) return;
    const initialize = () => {
      if (!window.google || !googleButtonRef.current) return;
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: ({ credential }) => void handleGoogleCredential(credential),
      });
      googleButtonRef.current.replaceChildren();
      window.google.accounts.id.renderButton(googleButtonRef.current, {
        theme: "outline", size: "large", text: "continue_with", shape: "rectangular", width: 360,
      });
    };
    let script = document.getElementById("google-identity-services") as HTMLScriptElement | null;
    if (!script) {
      script = document.createElement("script");
      script.id = "google-identity-services";
      script.src = "https://accounts.google.com/gsi/client";
      script.async = true;
      script.defer = true;
      script.addEventListener("load", initialize, { once: true });
      document.head.appendChild(script);
    } else if (window.google) initialize();
    else script.addEventListener("load", initialize, { once: true });
  }, []);

  async function handlePasswordLogin(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const result = await api.login(email.trim(), password);
      await finishSignIn(result.access_token);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Đăng nhập không thành công.");
    } finally {
      setBusy(false);
    }
  }

  async function refreshProfile() {
    try { setProfile(await api.getCurrentUser()); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Không tải được hồ sơ."); }
  }

  function logout() {
    setToken("");
    setProfile(null);
    setPassword("");
    setError("");
  }

  if (profile?.role === "admin") {
    return <main className="min-h-screen max-w-4xl mx-auto p-4 sm:p-6 space-y-5">
      <header className="soft-card p-5 flex flex-wrap items-center justify-between gap-3">
        <div><p className="text-xs text-[var(--muted)]">Khu vực quản trị</p><h1 className="text-xl font-semibold">Duyệt hồ sơ bác sĩ</h1></div>
        <span className="flex gap-3"><Link href="/" className="text-xs text-[var(--primary)] underline self-center">Mở trang bệnh nhân</Link><button className="btn-outline h-9 px-3 text-xs" onClick={logout}>Đăng xuất</button></span>
      </header>
      {error && <p role="alert" className="text-sm text-[#be123c]">{error}</p>}
      <AdminDoctorQueue api={api} />
    </main>;
  }

  if (profile?.doctor_status === "pending" || profile?.doctor_status === "active") {
    return <DoctorPortal api={api} onLogout={logout} status={profile.doctor_status}
      onStatusChange={(status) => setProfile((current) => current ? { ...current, doctor_status: status } : current)} />;
  }

  if (profile) {
    return <main className="min-h-screen max-w-3xl mx-auto p-4 sm:p-6 space-y-5">
      <header className="soft-card p-5 flex flex-wrap items-center justify-between gap-3">
        <div><p className="text-xs text-[var(--muted)]">Đăng nhập: {profile.email || profile.display_name}</p><h1 className="text-xl font-semibold">Đăng ký vào cổng bác sĩ</h1></div>
        <button className="btn-outline h-9 px-3 text-xs" onClick={logout}>Đăng xuất</button>
      </header>
      {error && <p role="alert" className="text-sm text-[#be123c]">{error}</p>}
      <DoctorApplication api={api} onSubmitted={() => void refreshProfile()} />
      {process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID && <section className="soft-card p-4 space-y-2">
        <p className="text-xs text-[var(--muted)]">Nếu tài khoản này chưa được xác minh email bằng Google, hãy liên kết bằng nút dưới trước khi gửi hồ sơ.</p>
        <div ref={googleButtonRef} className="min-h-10" />
      </section>}
      <Link href="/" className="block text-center text-xs text-[var(--primary)] underline">Quay lại trang mẹ bầu</Link>
    </main>;
  }

  return <main className="min-h-screen flex items-center justify-center p-4">
    <section className="soft-card w-full max-w-md p-6 space-y-5">
      <header className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-[var(--primary)] text-white flex items-center justify-center"><HeartPulse className="w-5 h-5" /></div>
        <div><h1 className="text-lg font-semibold">Cổng bác sĩ</h1><p className="text-xs text-[var(--muted)]">Đăng nhập riêng để xem các phiếu được mẹ bầu cấp quyền</p></div>
      </header>
      {error && <p role="alert" className="rounded-lg bg-[#fff1f2] p-3 text-sm text-[#be123c]">{error}</p>}
      {process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID ? <div className="flex flex-col items-center gap-2"><div ref={googleButtonRef} className="min-h-10" /><p className="text-[10px] text-[var(--muted)]">Đăng ký hồ sơ bác sĩ yêu cầu email đã xác minh bằng Google.</p></div> : <p className="rounded-lg bg-[#fffbeb] p-3 text-xs text-[#8a5b10]">Đăng nhập Google chưa được cấu hình. Hãy cấu hình NEXT_PUBLIC_GOOGLE_CLIENT_ID để bác sĩ xác minh email và đăng ký.</p>}
      <div className="flex items-center gap-3 text-[11px] text-[var(--muted)]"><span className="h-px flex-1 bg-[var(--border-strong)]" />hoặc đăng nhập tài khoản hiện có<span className="h-px flex-1 bg-[var(--border-strong)]" /></div>
      <form onSubmit={handlePasswordLogin} className="space-y-3">
        <label className="block text-xs">Email hoặc tên đăng nhập<input className="wf-input mt-1" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="username" required /></label>
        <label className="block text-xs">Mật khẩu<input className="wf-input mt-1" type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" required /></label>
        <button className="btn-outline w-full h-10 text-xs" disabled={busy}>{busy ? "Đang đăng nhập…" : "Đăng nhập"}</button>
      </form>
      <p className="text-center text-xs text-[var(--muted)]">Chưa có tài khoản? Dùng Google ở trên để tạo tài khoản, rồi gửi thông tin hành nghề để admin xác minh.</p>
      <Link href="/" className="block text-center text-xs text-[var(--primary)] underline">Quay lại trang mẹ bầu</Link>
    </section>
  </main>;
}
