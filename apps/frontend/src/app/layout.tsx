import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "Zelene", description: "Strategic Intelligence Presence" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="mesh-bg">{children}</body>
    </html>
  );
}
