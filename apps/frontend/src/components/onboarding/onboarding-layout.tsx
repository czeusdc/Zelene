"use client";
import { ZeleneAvatar } from "./zelene-avatar";
import { ProgressIndicator } from "./progress-indicator";

export function OnboardingLayout({ children, stage, isThinking }: {
  children: React.ReactNode; stage: string; isThinking: boolean;
}) {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex items-center justify-between px-8 py-6">
        <ZeleneAvatar isThinking={isThinking} />
        <ProgressIndicator stage={stage} />
      </header>
      {children}
    </div>
  );
}
