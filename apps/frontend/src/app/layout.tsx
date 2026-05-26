/**
 * @fileoverview Root layout — sets the HTML document shell, applies the
 * dark theme class and mesh background, and defines page metadata.
 * Part of the Zelene strategic intelligence platform.
 */

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
