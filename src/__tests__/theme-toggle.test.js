import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import ThemeToggle from "../components/ThemeToggle";

// ✅ use a "mock*" name so Jest allows it in the factory:
const mockToggle = jest.fn();
jest.mock("../hooks/useThemeMode", () => () => ({
  mode: "light",
  toggle: mockToggle,
}));

test("ThemeToggle calls toggle on click", () => {
  render(<ThemeToggle />);
  // icon button
  fireEvent.click(screen.getByRole("button"));
  expect(mockToggle).toHaveBeenCalledTimes(1);
});
