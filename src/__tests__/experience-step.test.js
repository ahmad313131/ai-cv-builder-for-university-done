import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import ExperienceStep from "../components/steps/ExperienceStep";

test("ExperienceStep renders and calls handleChange on typing", () => {
  const handleChange = jest.fn();
  const formData = {
    experience: "Intern @ ACME — React/Node",
  };

  render(<ExperienceStep formData={formData} handleChange={handleChange} />);

  // also stay generic here
  const boxes = screen.getAllByRole("textbox");
  expect(boxes.length).toBeGreaterThan(0);

  fireEvent.change(boxes[0], { target: { value: "Edited experience" } });
  expect(handleChange).toHaveBeenCalled();
});
