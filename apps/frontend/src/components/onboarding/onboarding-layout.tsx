/**
 * @fileoverview Shell layout for the onboarding flow.
 * Renders the Zelene avatar, progress indicator header, and child content.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { ZeleneAvatar } from "./zelene-avatar";
import { ProgressIndicator } from "./progress-indicator";

/**
 * OnboardingLayout — wraps onboarding step content with a header
 * containing the avatar and stage progress dots.
 */
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
