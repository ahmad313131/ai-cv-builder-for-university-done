import { Box, TextField, Button, Typography, Avatar, CircularProgress } from "@mui/material";

export default function PersonalInfoStep({
  formData,
  handleChange,
  photoUrl,
  handlePhotoChange,
  uploading,
  uploadError,
}) {
  return (
    <Box>
      <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
        <Avatar src={photoUrl} sx={{ width: 76, height: 76 }} />
        <div>
          <Button variant="outlined" component="label" disabled={uploading}>
            {uploading ? (
              <>
                Uploading...
                <CircularProgress size={16} sx={{ ml: 1 }} />
              </>
            ) : (
              "Upload Photo"
            )}
            <input type="file" hidden accept="image/*" onChange={handlePhotoChange} />
          </Button>
          {formData.photo_path && (
            <Typography variant="caption" display="block">
              Stored at: {formData.photo_path}
            </Typography>
          )}
          {uploadError && (
            <Typography variant="caption" color="error" display="block" sx={{ mt: 0.5 }}>
              {uploadError}
            </Typography>
          )}
        </div>
      </Box>

      <TextField
        fullWidth
        margin="normal"
        label="Name"
        name="name"
        value={formData.name}
        onChange={handleChange}
        autoComplete="name"
      />
      <TextField
        fullWidth
        margin="normal"
        type="email"
        label="Email"
        name="email"
        value={formData.email}
        onChange={handleChange}
        autoComplete="email"
      />
    </Box>
  );
}
