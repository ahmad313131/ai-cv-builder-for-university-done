import React from "react";
import { render, screen } from "@testing-library/react";
import AnalysisCard from "../components/AnalysisCard";

test("renders analysis details", () => {
  const analysis = {
    matching_score: 73.5,
    match_level: "Medium Match",
    reasons: ["Overlap ok", "Categories aligned"],
    missing_skills: ["Node.js", "Docker"],
    nice_to_have: ["Redux"],
  };
  render(<AnalysisCard analysis={analysis} analyzeError={null} />);

  // The score is rendered as 74% (rounded)
  expect(screen.getAllByText(/74/).length).toBeGreaterThan(0);
  expect(screen.getByText(/medium match/i)).toBeInTheDocument();
  expect(screen.getByText(/overlap ok/i)).toBeInTheDocument();
  expect(screen.getByText(/node\.js/i)).toBeInTheDocument();
  expect(screen.getByText(/redux/i)).toBeInTheDocument();
});
