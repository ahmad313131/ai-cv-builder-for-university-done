import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import EducationStep from "../components/steps/EducationStep";

test("EducationStep renders and calls handleChange on typing", () => {
  const handleChange = jest.fn();
  const formData = {
    education: "BSc CS — LIU (2021–2025)",
  };

  render(<EducationStep formData={formData} handleChange={handleChange} />);

  // be generic: grab the first textbox and type
  const boxes = screen.getAllByRole("textbox");
  expect(boxes.length).toBeGreaterThan(0);

  fireEvent.change(boxes[0], { target: { value: "Edited education" } });
  expect(handleChange).toHaveBeenCalled();
});
