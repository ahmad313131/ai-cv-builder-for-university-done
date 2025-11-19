import { Box, TextField } from "@mui/material";

export default function SkillsLinksStep({ formData, handleChange }) {
  return (
    <Box>
      <TextField
        fullWidth
        margin="normal"
        label="Skills (comma separated)"
        name="skills"
        value={formData.skills}
        onChange={handleChange}
        placeholder="Python, React, SQL"
      />
      <TextField
        fullWidth
        margin="normal"
        label="Languages (comma separated)"
        name="languages"
        value={formData.languages}
        onChange={handleChange}
        placeholder="English: Proficient, Arabic: Native"
      />
      <TextField
        fullWidth
        margin="normal"
        label="Hobbies (comma separated)"
        name="hobbies"
        value={formData.hobbies}
        onChange={handleChange}
        placeholder="Reading, Football, Music"
      />
      <TextField
        fullWidth
        margin="normal"
        label="GitHub"
        name="github"
        value={formData.github}
        onChange={handleChange}
      />
      <TextField
        fullWidth
        margin="normal"
        label="LinkedIn"
        name="linkedin"
        value={formData.linkedin}
        onChange={handleChange}
      />
      
      <TextField
        fullWidth
        margin="normal"
        label="Enter the job description you're applying for"
        name="job_description"
        multiline   // <-- أضفها
        rows={4}
        value={formData.job_description}
        onChange={handleChange}
      />

    </Box>
  );
}
