import React from "react";
import { render, screen } from "@testing-library/react";
import AppRouter from "../AppRouter";
import { ThemeModeProvider } from "../hooks/useThemeMode";
import { MemoryRouter } from "react-router-dom";
test("AppRouter renders Home without crashing", () => {
  render(
    <ThemeModeProvider>
      <MemoryRouter initialEntries={["/"]}>
        <AppRouter />
      </MemoryRouter>
    </ThemeModeProvider>
  );
  // Header shows "AI CV Builder" on Home
  expect(screen.getByText(/AI CV Builder/i)).toBeInTheDocument();
});
