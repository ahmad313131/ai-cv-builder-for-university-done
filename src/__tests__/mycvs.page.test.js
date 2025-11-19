import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import MyCVs from "../pages/MyCVs";
import { listCVs, getCV, downloadCV } from "../api";
jest.mock("../api", () => ({
  listCVs: jest.fn(() => Promise.resolve([])),
  getCV: jest.fn(() =>
    Promise.resolve({ id: 1, name: "Alex J", email: "a@a.com" })
  ),
  downloadCV: jest.fn(() => Promise.resolve()),
}));

function renderMyCVs() {
  return render(
    <MemoryRouter>
      <MyCVs />
    </MemoryRouter>
  );
}

describe("MyCVs page", () => {
  afterEach(() => jest.clearAllMocks());

  test("shows loader then empty state", async () => {
    renderMyCVs();
    expect(screen.getByRole("progressbar")).toBeInTheDocument();
    expect(await screen.findByText(/no saved cvs yet/i)).toBeInTheDocument();
  });

  test("renders a list and triggers PDF download", async () => {
    listCVs.mockResolvedValueOnce([
      {
        id: 11,
        name: "Alex CV",
        email: "a@a.com",
        created_at: "2025-11-19T10:10:10Z",
      },
    ]);

    renderMyCVs();

    // Wait for list item
    expect(await screen.findByText(/Alex CV/i)).toBeInTheDocument();

    // Click PDF icon button
    const pdfBtn = screen.getByLabelText(/pdf/i);
    fireEvent.click(pdfBtn);

    await waitFor(() => expect(getCV).toHaveBeenCalledWith(11));
    expect(downloadCV).toHaveBeenCalled();
    const args = downloadCV.mock.calls[0];
    expect(args[0]).toEqual({ id: 1, name: "Alex J", email: "a@a.com" }); // from getCV mock
    expect(args[1]).toMatch(/^cv_11_/); // filename contains id
  });

  test("handles API error", async () => {
    listCVs.mockRejectedValueOnce(new Error("boom"));
    renderMyCVs();
    expect(await screen.findByText(/boom/i)).toBeInTheDocument();
  });
});
