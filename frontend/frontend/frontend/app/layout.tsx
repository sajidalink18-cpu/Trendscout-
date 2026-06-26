import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TrendScout AI",
  description: "AI-powered business opportunity scanner",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ background: "#040912", color: "#f1f5f9", fontFamily: "system-ui, sans-serif", margin: 0 }}>
        {children}
      </body>
    </html>
  );
}
