import React from "react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { render, screen } from "@testing-library/react";
import PrivateRoute from "../PrivateRoute";

// Mock token helper to control auth state
jest.mock("../api", () => ({
  getToken: jest.fn(() => null),
}));

const Secret = () => <div>SECRET-AREA</div>;
const Login = () => <div>LOGIN-PAGE</div>;

describe("PrivateRoute", () => {
  afterEach(() => jest.resetAllMocks());

  test("redirects to /login when no token", () => {
    // default mock is null (unauth)
    render(
      <MemoryRouter initialEntries={["/private"]}>
        <Routes>
          <Route
            path="/private"
            element={
              <PrivateRoute>
                <Secret />
              </PrivateRoute>
            }
          />
          <Route path="/login" element={<Login />} />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByText("LOGIN-PAGE")).toBeInTheDocument();
  });

  test("renders children when token exists", () => {
    const { getToken } = require("../api");
    getToken.mockReturnValue("tok"); // auth on

    render(
      <MemoryRouter initialEntries={["/private"]}>
        <Routes>
          <Route
            path="/private"
            element={
              <PrivateRoute>
                <Secret />
              </PrivateRoute>
            }
          />
          <Route path="/login" element={<Login />} />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByText("SECRET-AREA")).toBeInTheDocument();
  });
});
