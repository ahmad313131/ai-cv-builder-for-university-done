import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import UserMenu from "../components/UserMenu";
// ✅ use a "mock*" name so Jest allows it:
const mockNavigate = jest.fn();
jest.mock("react-router-dom", () => {
  const actual = jest.requireActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

// Mock API used by UserMenu
const mockLogout = jest.fn();
jest.mock("../api", () => ({
  me: jest.fn(() => Promise.resolve({ email: "a@a.com", username: "Alex" })),
  logout: (...args) => mockLogout(...args),
}));

test("UserMenu shows user then logs out", async () => {
  render(
    <MemoryRouter>
      <UserMenu />
    </MemoryRouter>
  );

  // wait for fetch of user (me)
  expect(await screen.findByText(/Signed in as/i)).toBeInTheDocument();
  expect(screen.getByText(/Alex/i)).toBeInTheDocument();

  // click Logout
  fireEvent.click(screen.getByRole("button", { name: /logout/i }));

  await waitFor(() => {
    expect(mockLogout).toHaveBeenCalledTimes(1);
    // eslint-disable-next-line testing-library/no-wait-for-multiple-assertions
    expect(mockNavigate).toHaveBeenCalledWith("/login", { replace: true });
  });
});
