// src/components/UploadForm.tsx
import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Box, Button, LinearProgress, Typography, Paper } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { uploadStart, uploadProgress, uploadSuccess, uploadFailure } from '../store/slices/uploadSlice';
import { RootState } from '../store';
import axios from 'axios';
import { toast } from 'react-toastify';

const UploadForm: React.FC = () => {
  const dispatch = useDispatch();
  const { isUploading, progress, error } = useSelector((state: RootState) => state.upload);
  const { token } = useSelector((state: RootState) => state.auth);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !token) {
      toast.error('Please select a file and ensure you are logged in');
      return;
    }

    const formData = new FormData();
    formData.append('video_file', selectedFile);

    dispatch(uploadStart());

    try {
      const response = await axios.post('/api/data/upload_video', formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
          dispatch(uploadProgress(progress));
        },
      });

      dispatch(uploadSuccess(response.data.video_id));
      toast.success('Video uploaded successfully!');
      setSelectedFile(null);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to upload video';
      dispatch(uploadFailure(errorMessage));
      toast.error(errorMessage);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Box sx={{ textAlign: 'center' }}>
        <input
          accept="video/*"
          style={{ display: 'none' }}
          id="video-upload"
          type="file"
          onChange={handleFileSelect}
          disabled={isUploading}
        />
        <label htmlFor="video-upload">
          <Button
            variant="contained"
            component="span"
            startIcon={<CloudUploadIcon />}
            disabled={isUploading}
          >
            Select Video
          </Button>
        </label>

        {selectedFile && (
          <Typography variant="body1" sx={{ mt: 2 }}>
            Selected file: {selectedFile.name}
          </Typography>
        )}

        {isUploading && (
          <Box sx={{ mt: 2 }}>
            <LinearProgress variant="determinate" value={progress} />
            <Typography variant="body2" sx={{ mt: 1 }}>
              Upload progress: {progress}%
            </Typography>
          </Box>
        )}

        {error && (
          <Typography color="error" sx={{ mt: 2 }}>
            {error}
          </Typography>
        )}

        <Button
          variant="contained"
          color="primary"
          onClick={handleUpload}
          disabled={!selectedFile || isUploading}
          sx={{ mt: 2 }}
        >
          Upload
        </Button>
      </Box>
    </Paper>
  );
};

export default UploadForm;