"use client";

import { useState } from "react";

const WARNING_SIGNS = [
  "Đau đầu dữ dội, kéo dài hoặc kèm nhìn mờ/chớp sáng",
  "Khó thở, đau ngực, tim đập nhanh bất thường hoặc ngất",
  "Đau bụng dữ dội không giảm",
  "Chảy máu âm đạo nhiều hơn vài đốm hoặc rỉ dịch",
  "Thai máy giảm rõ rệt hoặc ngừng so với thường ngày",
  "Sốt từ 38°C, hoặc nôn nhiều đến mức không giữ được nước",
  "Ý nghĩ làm hại bản thân hoặc em bé",
];

export function SymptomSafetyCheck() {
  const [selected, setSelected] = useState<string[]>([]);
  function toggle(item: string) {
    setSelected((current) => current.includes(item) ? current.filter((value) => value !== item) : [...current, item]);
  }
  return <details className="soft-card p-4 sm:p-5 space-y-3" aria-labelledby="maternal-safety-title">
    <summary id="maternal-safety-title" className="cursor-pointer font-semibold text-[15px]">Bạn đang có dấu hiệu cần liên hệ nhân viên y tế ngay?</summary>
    <div className="space-y-3">
      <p className="mt-1 text-xs leading-relaxed text-[var(--muted)]">Đây là danh sách nhắc an toàn trong thai kỳ, không phải công cụ chẩn đoán. Chọn dấu hiệu đang gặp để xem hướng xử lý. Thông tin chọn chỉ xử lý trên trình duyệt, không gửi cho AI hay lưu vào hồ sơ.</p>
    <div className="space-y-2">{WARNING_SIGNS.map((sign) => <label key={sign} className="flex gap-2 items-start rounded-lg bg-[#f8fafa] p-2.5 text-xs leading-5">
      <input type="checkbox" className="mt-1" checked={selected.includes(sign)} onChange={() => toggle(sign)} />{sign}
    </label>)}</div>
    {selected.length > 0 ? <div role="alert" className="rounded-xl border border-[#e9a3a3] bg-[#fff1f2] p-3 text-sm text-[#8f1d1d] space-y-2">
      <b>Hãy liên hệ cơ sở sản khoa/bác sĩ đang theo dõi ngay để được đánh giá.</b>
      <p className="text-xs">Nếu triệu chứng nặng hoặc diễn tiến nhanh, đến khoa cấp cứu hoặc gọi số cấp cứu y tế tại nơi chị đang ở. Đừng chờ AI đọc phiếu CBC hay tự trì hoãn việc đi khám.</p>
      <p className="text-[10px]">Nguồn: <a className="underline" href="https://www.cdc.gov/hearher/maternal-warning-signs/index.html" target="_blank" rel="noreferrer">CDC Hear Her — dấu hiệu cảnh báo khẩn cấp của mẹ</a>. Danh sách không bao quát mọi tình huống.</p>
    </div> : <p className="text-[10px] text-[var(--muted)]">Nếu chị vẫn thấy không ổn hoặc lo lắng, hãy liên hệ bác sĩ dù không thấy dấu hiệu trong danh sách.</p>}
    </div>
  </details>;
}
