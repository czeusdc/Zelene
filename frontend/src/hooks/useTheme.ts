/**
 * @fileoverview Theme management hook — persists user preference to localStorage
 * and toggles the `light` class on the document root. Uses the same `"theme"`
 * key as the FOUC-prevention script in layout.tsx and the landing page toggle
 * in page.tsx so all three stay in sync.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useState, useCallback } from "react";

/** localStorage key shared with layout.tsx (FOUC script) and page.tsx (toggle). */
const STORAGE_KEY = "theme";

type Theme = "dark" | "light";

function readInitialTheme(): Theme {
  if (typeof window === "undefined") return "dark";
  const legacy = localStorage.getItem("zelene-theme") as Theme | null;
  const stored = localStorage.getItem(STORAGE_KEY) as Theme | null;
  const resolved = stored || legacy;
  if (resolved === "dark" || resolved === "light") {
    document.documentElement.classList.toggle("light", resolved === "light");
    localStorage.setItem(STORAGE_KEY, resolved);
    if (legacy) localStorage.removeItem("zelene-theme");
    return resolved;
  }
  return "dark";
}

/**
 * useTheme — reads/writes theme preference from localStorage using the same
 * key ("theme") as the landing page. Handles migration from a legacy key
 * ("zelene-theme") for existing users. Initial state is read synchronously
 * to avoid setState-in-effect.
 */
export function useTheme() {
  const [theme, setThemeState] = useState<Theme>(readInitialTheme);

  const setTheme = useCallback((t: Theme) => {
    setThemeState(t);
    localStorage.setItem(STORAGE_KEY, t);
    document.documentElement.classList.toggle("light", t === "light");
  }, []);

  const toggleTheme = useCallback(() => {
    setTheme(theme === "dark" ? "light" : "dark");
  }, [theme, setTheme]);

  return { theme, setTheme, toggleTheme };
}
