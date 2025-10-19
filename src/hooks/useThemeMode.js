// src/hooks/useThemeMode.js
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { makeTheme } from "../theme";

const KEY = "app-theme-mode";
const ThemeModeCtx = createContext(null);

export function ThemeModeProvider({ children }) {
  const [mode, setMode] = useState(() => localStorage.getItem(KEY) || "light");

  useEffect(() => {
    localStorage.setItem(KEY, mode);
    // اختياري: sync مع class بالـhtml لو بدك
    document.documentElement.dataset.theme = mode;
  }, [mode]);

  const theme = useMemo(() => makeTheme(mode), [mode]);
  const toggle = () => setMode((m) => (m === "light" ? "dark" : "light"));

  const value = useMemo(
    () => ({ mode, setMode, toggle, theme }),
    [mode, theme]
  );

  return (
    <ThemeModeCtx.Provider value={value}>{children}</ThemeModeCtx.Provider>
  );
}

export default function useThemeMode() {
  const ctx = useContext(ThemeModeCtx);
  if (!ctx)
    throw new Error("useThemeMode must be used within <ThemeModeProvider>");
  return ctx;
}
