import React from "react";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import AppLayout from "../components/AppLayout";

// mock getToken so Header renders guest state safely
jest.mock("../api", () => ({
  getToken: () => null,
}));

test("AppLayout shows header and renders children via outlet", () => {
  render(
    <MemoryRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<div>CHILD-CONTENT</div>} />
        </Route>
      </Routes>
    </MemoryRouter>
  );

  // header title appears in your Header.jsx
  expect(screen.getByText(/AI CV Builder/i)).toBeInTheDocument();
  // outlet content
  expect(screen.getByText("CHILD-CONTENT")).toBeInTheDocument();
});
