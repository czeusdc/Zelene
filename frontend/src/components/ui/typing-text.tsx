/**
 * @fileoverview Typing text reveal component — animates text character-by-character
 * to create the illusion of a presence composing thoughts. Uses a module-level Set
 * to avoid re-animating messages that have already been revealed.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useState, useEffect, useRef } from "react";

/** Module-level Set tracking message IDs that have finished revealing. */
const revealedIds = new Set<string>();

/**
 * TypingText — reveals text character-by-character at ~30ms per character,
 * capped at 3 seconds total. Skips animation if the messageId has already
 * been revealed (e.g. on re-render or navigation back).
 */
export function TypingText({
  text,
  messageId,
  className,
  style,
  delay = 0,
  speed = 15,
  maxDuration = 3000,
}: {
  text: string;
  messageId: string;
  className?: string;
  style?: React.CSSProperties;
  delay?: number;
  speed?: number;
  maxDuration?: number;
}) {
  const [displayed, setDisplayed] = useState(() =>
    revealedIds.has(messageId) ? text : ""
  );
  const indexRef = useRef(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const isAlreadyRevealed = revealedIds.has(messageId);
  const adjustedSpeed = Math.max(speed, text.length > 0 ? maxDuration / text.length : speed);

  useEffect(() => {
    if (isAlreadyRevealed) return;

    const startTimeout = setTimeout(() => {
      intervalRef.current = setInterval(() => {
        indexRef.current += 1;
        if (indexRef.current >= text.length) {
          if (intervalRef.current) clearInterval(intervalRef.current);
          revealedIds.add(messageId);
          setDisplayed(text);
        } else {
          setDisplayed(text.slice(0, indexRef.current));
        }
      }, adjustedSpeed);
    }, delay);

    return () => {
      clearTimeout(startTimeout);
      if (intervalRef.current) clearInterval(intervalRef.current);
      // If unmounted before completion, mark as revealed so it doesn't restart
      if (indexRef.current > 0 && indexRef.current < text.length) {
        revealedIds.add(messageId);
      }
    };
  }, [text, messageId, delay, adjustedSpeed, isAlreadyRevealed]);

  return (
    <span className={className} style={style}>
      {displayed}
      {!isAlreadyRevealed && displayed.length < text.length && (
        <span className="animate-pulse-soft">|</span>
      )}
    </span>
  );
}
