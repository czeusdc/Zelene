/**
 * @fileoverview Shell layout for the onboarding flow.
 * Renders the Zelene avatar, progress indicator header, and child content.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useState, useEffect } from "react";
import { ZeleneAvatar } from "./zelene-avatar";
import { ProgressIndicator } from "./progress-indicator";

/**
 * OnboardingLayout — wraps onboarding step content with a header
 * containing the avatar, stage progress, and a theme toggle.
 */
export function OnboardingLayout({ children, stage, isThinking }: {
  children: React.ReactNode; stage: string; isThinking: boolean;
}) {
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    setIsDark(document.documentElement.classList.contains("dark"));
  }, []);

  const toggleTheme = () => {
    const html = document.documentElement;
    if (html.classList.contains("dark")) {
      html.classList.remove("dark");
      html.classList.add("light");
      localStorage.setItem("theme", "light");
      setIsDark(false);
    } else {
      html.classList.remove("light");
      html.classList.add("dark");
      localStorage.setItem("theme", "dark");
      setIsDark(true);
    }
  };

  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex items-center justify-between px-8 py-6">
        <ZeleneAvatar isThinking={isThinking} />
        <div className="flex items-center gap-4">
          <ProgressIndicator stage={stage} />
          <button
            onClick={toggleTheme}
            className="text-xs uppercase tracking-widest transition-all hover:brightness-125"
            style={{ color: "hsl(var(--text-secondary))" }}
          >
            {isDark ? "Light" : "Dark"}
          </button>
        </div>
      </header>
      {children}
    </div>
  );
}
