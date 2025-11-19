import React from "react";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Header from "../components/Header";

// keep it simple: guest state, avoid login-dependent branches
jest.mock("../api", () => ({
  getToken: () => null,
}));

test("Header renders app title and theme toggle", () => {
  render(
    <MemoryRouter>
      <Header />
    </MemoryRouter>
  );
  expect(screen.getByText(/AI CV Builder/i)).toBeInTheDocument();
  // ThemeToggle has data-testid="theme-toggle" in your component
  expect(screen.getByTestId("theme-toggle")).toBeInTheDocument();
});
