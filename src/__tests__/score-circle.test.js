import React from "react";
import { render, screen } from "@testing-library/react";
import ScoreCircle from "../components/ScoreCircle";

describe("ScoreCircle", () => {
  test("renders rounded percent inside the SVG", () => {
    render(<ScoreCircle value={73.5} />);
    // it renders text nodes "74" and "%"
    expect(screen.getAllByText(/74/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/%/).length).toBeGreaterThan(0);
  });

  test("clamps values <0 and >100", () => {
    render(<ScoreCircle value={-10} />);
    expect(screen.getAllByText(/0/).length).toBeGreaterThan(0);

    render(<ScoreCircle value={200} />);
    expect(screen.getAllByText(/100/).length).toBeGreaterThan(0);
  });
});
