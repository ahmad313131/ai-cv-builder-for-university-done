import React from "react";
import { render, screen } from "@testing-library/react";
import ScoreBar from "../components/ScoreBar";

describe("ScoreBar", () => {
  test("renders label and percent", () => {
    render(<ScoreBar value={55} label="Matching Score" />);
    expect(screen.getByText(/Matching Score/i)).toBeInTheDocument();
    // label or numeric render; tolerant check:
    expect(screen.getAllByText(/55/).length).toBeGreaterThan(0);
  });

  test("handles zero and hundred", () => {
    const { rerender } = render(<ScoreBar value={0} label="L" />);
    expect(screen.getAllByText(/0/).length).toBeGreaterThan(0);
    rerender(<ScoreBar value={100} label="L" />);
    expect(screen.getAllByText(/100/).length).toBeGreaterThan(0);
  });
});
