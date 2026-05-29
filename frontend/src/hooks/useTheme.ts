/**
 * @fileoverview Theme management hook — persists user preference to localStorage
 * and toggles the `light` class on the document root. Uses the same `"theme"`
 * key as the FOUC-prevention script in layout.tsx and the landing page toggle
 * in page.tsx so all three stay in sync.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useState, useEffect, useCallback } from "react";

/** localStorage key shared with layout.tsx (FOUC script) and page.tsx (toggle). */
const STORAGE_KEY = "theme";

type Theme = "dark" | "light";

/**
 * useTheme — reads/writes theme preference from localStorage using the same
 * key ("theme") as the landing page. Handles migration from a legacy key
 * ("zelene-theme") for existing users.
 */
export function useTheme() {
  const [theme, setThemeState] = useState<Theme>("dark");

  useEffect(() => {
    // Migrate legacy "zelene-theme" key if present, then always use "theme"
    const legacy = localStorage.getItem("zelene-theme") as Theme | null;
    const stored = localStorage.getItem(STORAGE_KEY) as Theme | null;
    const resolved = stored || legacy;

    if (resolved && (resolved === "dark" || resolved === "light")) {
      setThemeState(resolved);
      document.documentElement.classList.toggle("light", resolved === "light");
      // Persist resolved value under canonical key and clean up legacy
      localStorage.setItem(STORAGE_KEY, resolved);
      if (legacy) localStorage.removeItem("zelene-theme");
    }
  }, []);

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
