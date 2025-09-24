"use client";
import { useEffect, useState } from "react";

const STORAGE_KEY = "area.theme";

export default function ThemeToggle() {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    // Initialize from storage or prefers-color-scheme
    const stored = (typeof window !== 'undefined') ? localStorage.getItem(STORAGE_KEY) : null;
    if (stored === "light" || stored === "dark") {
      setTheme(stored);
      document.documentElement.setAttribute("data-theme", stored);
    } else {
      const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      const initial = prefersDark ? "dark" : "light";
      setTheme(initial);
      document.documentElement.setAttribute("data-theme", initial);
    }
  }, []);

  function toggle() {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem(STORAGE_KEY, next);
  }

  return (
    <button onClick={toggle} className="btn" aria-label="Toggle theme">
      {theme === 'light' ? '🌙 Dark' : '☀️ Light'}
    </button>
  );
}
