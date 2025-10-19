import { TextField } from "@mui/material";

export default function ExperienceStep({ formData, handleChange }) {
  return (
    <TextField
      fullWidth
      multiline
      minRows={6}
      margin="normal"
      label="Experience"
      name="experience"
      value={formData.experience}
      onChange={handleChange}
      placeholder="Use bullet-like lines or separate by new lines"
    />
  );
}
