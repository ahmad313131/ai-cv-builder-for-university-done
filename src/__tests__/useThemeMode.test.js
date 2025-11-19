import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import useThemeMode, { ThemeModeProvider } from "../hooks/useThemeMode";

function HookProbe() {
  const { mode, toggle } = useThemeMode();
  return (
    <div>
      <span data-testid="mode">{mode}</span>
      <button onClick={toggle}>toggle</button>
    </div>
  );
}

beforeEach(() => {
  localStorage.clear();
  document.documentElement.dataset.theme = "";
});

test("reads initial mode from localStorage and syncs dataset", () => {
  localStorage.setItem("app-theme-mode", "dark");

  render(
    <ThemeModeProvider>
      <HookProbe />
    </ThemeModeProvider>
  );

  expect(screen.getByTestId("mode")).toHaveTextContent("dark");
  expect(document.documentElement.dataset.theme).toBe("dark");
});

test("toggle flips mode and updates dataset", () => {
  render(
    <ThemeModeProvider>
      <HookProbe />
    </ThemeModeProvider>
  );

  // default "light"
  expect(screen.getByTestId("mode")).toHaveTextContent("light");

  fireEvent.click(screen.getByText("toggle"));
  expect(screen.getByTestId("mode")).toHaveTextContent("dark");
  expect(document.documentElement.dataset.theme).toBe("dark");
});
