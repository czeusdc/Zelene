/**
 * @fileoverview Relative time display — shows human-readable elapsed time
 * ("just now", "1m ago", "3m ago") and updates every 30 seconds.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useState, useEffect } from "react";

function formatRelativeTime(dateString: string): string {
  if (!dateString) return "";
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return "";
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffSec < 30) return "just now";
  if (diffMin < 1) return "<1m ago";
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHour < 24) return `${diffHour}h ago`;
  return `${diffDay}d ago`;
}

/**
 * RelativeTime — renders a human-readable elapsed time string that
 * re-computes every 30 seconds to stay current.
 */
export function RelativeTime({ dateString }: { dateString: string }) {
  const [, setTick] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => setTick((t) => t + 1), 30000);
    return () => clearInterval(interval);
  }, []);

  return <span>{formatRelativeTime(dateString)}</span>;
}
