/**
 * @fileoverview Top bar of the strategic-intelligence View.
 * Shows the Zelene logo and a settings gear button.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";

/**
 * ViewHeader — renders the View's top bar with Zelene title
 * and a settings button that invokes the parent callback.
 */
export function ViewHeader({ onSettingsClick }: { onSettingsClick: () => void }) {
  return (
    <header className="flex items-center justify-between px-6 py-2 border-b" style={{ borderColor: "hsl(var(--text-muted) / 0.1)" }}>
      <h1 className="text-base font-normal uppercase tracking-widest" style={{ letterSpacing: "0.18em" }}>
        {"Z E L E N E".split(" ").map((char, i) =>
          i === 1 || i === 3 ? (
            <span key={i} style={{ color: "hsl(var(--accent-secondary))", animation: "letter-breath 3s ease-in-out infinite" }}>{char} </span>
          ) : (
            <span key={i}>{char} </span>
          )
        )}
      </h1>
      <button onClick={onSettingsClick} className="rounded-lg p-1.5 transition-all hover:brightness-125" style={{ color: "hsl(var(--text-muted))", fontSize: 24, lineHeight: 1 }}>{"\u2699"}</button>
    </header>
  );
}
