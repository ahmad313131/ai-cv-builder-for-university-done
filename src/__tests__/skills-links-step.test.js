import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import SkillsLinksStep from "../components/steps/SkillsLinksStep";

test("renders skills/links fields and calls handleChange", () => {
  const handleChange = jest.fn();
  const formData = {
    skills: "React, SQL",
    languages: "English, Arabic",
    hobbies: "Football",
    github: "https://github.com/u",
    linkedin: "https://linkedin.com/in/u",
    job_description: "JD here",
  };

  render(<SkillsLinksStep formData={formData} handleChange={handleChange} />);

  // presence
  const skills = screen.getByLabelText(/Skills \(comma separated\)/i);
  const languages = screen.getByLabelText(/Languages \(comma separated\)/i);
  const hobbies = screen.getByLabelText(/Hobbies \(comma separated\)/i);
  const github = screen.getByLabelText(/GitHub/i);
  const linkedin = screen.getByLabelText(/LinkedIn/i);
  const jd = screen.getByLabelText(/Enter the job description/i);

  // change events
  fireEvent.change(skills, { target: { value: "React, Node" } });
  fireEvent.change(languages, { target: { value: "EN, AR" } });
  fireEvent.change(hobbies, { target: { value: "Reading" } });
  fireEvent.change(github, { target: { value: "https://g/u2" } });
  fireEvent.change(linkedin, { target: { value: "https://li/u2" } });
  fireEvent.change(jd, { target: { value: "New JD" } });

  expect(handleChange).toHaveBeenCalledTimes(6);

  // textarea hint: multiline
  expect(jd.tagName.toLowerCase()).toBe("textarea");
});
