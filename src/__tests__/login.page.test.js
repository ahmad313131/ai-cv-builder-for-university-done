import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Login from "../pages/Login";
import { login, register as apiRegister, me } from "../api";
let mockNavigate = jest.fn();
jest.mock("react-router-dom", () => {
  const actual = jest.requireActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useSearchParams: () => [new URLSearchParams("")],
  };
});

jest.mock("../api", () => ({
  login: jest.fn(() => Promise.resolve({ access_token: "t" })),
  register: jest.fn(() => Promise.resolve({ id: 1 })),
  me: jest.fn(() => Promise.resolve({ id: 1, email: "x@x.com" })),
}));

describe("Login page", () => {
  afterEach(() => {
    jest.clearAllMocks();
    mockNavigate = jest.fn();
  });

  test("login mode: submits identifier + password and navigates", async () => {
    render(
      <MemoryRouter initialEntries={["/login"]}>
        <Login />
      </MemoryRouter>
    );

    // ...same imports/mocks as you had

    // login mode
    fireEvent.change(
      screen.getByRole("textbox", { name: /email or username/i }),
      { target: { value: "user@site.com" } }
    );
    fireEvent.change(
      screen.getByLabelText(/password/i, { selector: "input" }),
      { target: { value: "secret" } }
    );
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

    // register mode
    fireEvent.click(screen.getByRole("button", { name: /create one/i }));

    fireEvent.change(screen.getByLabelText(/email/i, { selector: "input" }), {
      target: { value: "new@site.com" },
    });
    fireEvent.change(
      screen.getByLabelText(/username/i, { selector: "input" }),
      { target: { value: "newuser" } }
    );
    fireEvent.change(
      screen.getByLabelText(/password/i, { selector: "input" }),
      { target: { value: "pass1234" } }
    );

    // Switch to register
    fireEvent.click(screen.getByRole("button", { name: /create one/i }));

    fireEvent.change(screen.getByLabelText(/^email$/i), {
      target: { value: "new@site.com" },
    });
    fireEvent.change(screen.getByLabelText(/username/i), {
      target: { value: "newuser" },
    });
    fireEvent.change(screen.getByLabelText(/^password$/i), {
      target: { value: "pw123" },
    });
    fireEvent.click(screen.getByRole("button", { name: /sign up/i }));

    await waitFor(() =>
      expect(apiRegister).toHaveBeenCalledWith(
        "new@site.com",
        "pw123",
        "newuser"
      )
    );
    expect(login).toHaveBeenCalledWith("new@site.com", "pw123");
    expect(me).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith("/builder", { replace: true });
  });
});
