import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Home from "../pages/Home";
import { ThemeModeProvider } from "../hooks/useThemeMode";

jest.mock("../api", () => ({
  getToken: jest.fn(() => null),
  me: jest.fn(() => Promise.resolve({ email: "u@x.com", username: "u" })),
}));

const { getToken, me } = jest.requireMock("../api");

function renderHome() {
  return render(
    <ThemeModeProvider>
      <MemoryRouter initialEntries={["/"]}>
        <Home />
      </MemoryRouter>
    </ThemeModeProvider>
  );
}

test("Home page • shows CTA for guests", () => {
  getToken.mockReturnValue(null);

  renderHome();

  expect(screen.getByText(/AI CV Builder/i)).toBeInTheDocument();

  // They are <a> links (MUI Button with component=Link)
  expect(screen.getByRole("link", { name: /log in/i })).toBeInTheDocument();
  expect(
    screen.getByRole("link", { name: /continue without login/i })
  ).toBeInTheDocument();
});

test("Home page • shows 'Open Builder' and 'My CVs' for signed users", async () => {
  getToken.mockReturnValue("token123");
  me.mockResolvedValue({ email: "user@site.com", username: "Alex" });

  renderHome();

  await waitFor(() => expect(me).toHaveBeenCalled());

  // Auth CTAs are also links
  expect(
    screen.getByRole("link", { name: /open builder/i })
  ).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /my cvs/i })).toBeInTheDocument();
});
