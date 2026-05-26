/**
 * @fileoverview Theme management hook — persists user preference to localStorage
 * and toggles the `light` class on the document root.
 * Part of the Zelene strategic intelligence platform.
 */

"use client";
import { useState, useEffect, useCallback } from "react";

type Theme = "dark" | "light";

/**
 * useTheme — reads/writes theme preference from localStorage and
 * returns the current theme, a setter, and a toggle function.
 */
export function useTheme() {
  const [theme, setThemeState] = useState<Theme>("dark");

  useEffect(() => {
    const stored = localStorage.getItem("zelene-theme") as Theme | null;
    if (stored) {
      setThemeState(stored);
      document.documentElement.classList.toggle("light", stored === "light");
    }
  }, []);

  const setTheme = useCallback((t: Theme) => {
    setThemeState(t);
    localStorage.setItem("zelene-theme", t);
    document.documentElement.classList.toggle("light", t === "light");
  }, []);

  const toggleTheme = useCallback(() => {
    setTheme(theme === "dark" ? "light" : "dark");
  }, [theme, setTheme]);

  return { theme, setTheme, toggleTheme };
}
