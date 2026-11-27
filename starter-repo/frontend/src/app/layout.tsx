import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin", "vietnamese"],
  weight: ["400", "500", "600"],
  variable: "--font-inter",
});

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
    <html lang="vi" className={inter.variable}>
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
