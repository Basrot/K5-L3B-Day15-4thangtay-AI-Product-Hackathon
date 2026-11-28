import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Đọc phiếu CBC thai kỳ · 4thangtay",
  description:
    "Trợ lý đọc hiểu 8 chỉ số công thức máu (CBC) cho thai phụ theo tam cá nguyệt, hỗ trợ OCR và hỏi đáp giọng nói tiếng Việt.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
